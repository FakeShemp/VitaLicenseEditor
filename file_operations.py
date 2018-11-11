#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os import path, stat
import mmap

psv_offset = 512
unk_pos = 0x1C00
unk_len = 0x260
lic1_offset = 0x40
lic1_len = 0x10
lic2_offset = 0x50
lic2_len = 0x160
license_header = bytes.fromhex('FFFF0001000104020000000000000000')


class VleFileOperations:
    def __init__(self, gui, app):
        self.psv_header_len = None
        self.license_position = None
        self.file_size = None
        self.gui = gui
        self.app = app

    def strip_psv(self):
        if self._sanity_check():
            self._copy_file(self.gui.get_psv_directory(), self.gui.get_output_directory())

    def _sanity_check(self):
        self.psv_header_len = None
        self.license_position = None
        self.file_size = None
        self.gui.status.clear()

        if not self.gui.get_psv_directory():
            self._add_message("Input path is empty!")
            return None
        if not self._check_if_path_is_file(self.gui.get_psv_directory()):
            self._add_message("Input file is not an existing file!")
            return None
        return self._read_file_properties(self.gui.get_psv_directory())

    @staticmethod
    def _check_if_path_is_file(file_path):
        return path.isfile(file_path)

    def _check_if_strippable_psv_file(self, file):
        header = file.read(3)
        file.seek(0)

        if header == b'PSV':
            self._add_message("PSV header found in input file...")
            return True
        else:
            return False

    def _read_file_properties(self, file_path):
        self.file_size = stat(file_path).st_size

        file = open(file_path, 'rb')

        if self._check_if_strippable_psv_file(file):
            self.psv_header_len = self._read_psv_header_len(file)
            self._add_message("PSV header length found to be: " + str(self.psv_header_len) + " bytes")
        else:
            self._add_message("Input file is not a valid PSV file!", True)
            file.close()
            return None

        self.license_position = self._find_license(file)

        if self.license_position:
            self._add_message("License found at position: " + str(hex(self.license_position)))
        else:
            self._add_message("No license found in input file!", True)
            file.close()
            return None

        file.close()

        return True

    @staticmethod
    def _read_psv_header_len(file):
        file.seek(0x68)
        length = ord(file.read(1)) * psv_offset
        file.seek(0)
        return length

    def _find_license(self, file):
        self._add_message("Scanning input for license file. Please wait...")
        with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
            pos = s.find(license_header)
            if pos:
                return pos + 0x10
        return None

    def _copy_file(self, input_file, output_file):
        self._add_message("Writing output file. Please wait...")

        with open(input_file, 'rb') as _input, open(output_file, 'wb') as _output:
            _input.seek(self.psv_header_len)  # Ignore PSV header

            self._copy_data(_input, _output, _len=unk_pos)  # Read up to UNKNOWN
            self._copy_data(_input, _output, _len=unk_len, zeroed=True)  # Zero out UNKNOWN
            self._copy_data(_input,
                            _output,
                            _len=self.license_position + lic1_offset - _input.tell())  # Read up to License1
            self._copy_data(_input,
                            _output,
                            _len=lic1_len, zeroed=True)  # Zero out first license part
            self._copy_data(_input,
                            _output,
                            _len=lic2_offset)  # Read up to License2
            self._copy_data(_input,
                            _output,
                            _len=lic2_len, zeroed=True)  # Zero out second license part
            self._copy_data(_input,
                            _output,
                            _len=self.file_size - _input.tell())  # Read to EOF

        self._add_message("File written!")

    @staticmethod
    def _copy_data(_input, _output, _len, zeroed=False):
        pass_length = _len
        bufsize = 1024 * 1024 * 10

        while pass_length:
            chunk = min(bufsize, pass_length)
            if zeroed:
                _input.read(chunk)
                data = b"".rjust(chunk, b"\x00")
            else:
                data = _input.read(chunk)
            _output.write(data)
            pass_length -= chunk

    def _add_message(self, message, clear=False):
        # TODO - Make status window read-only
        if clear:
            self.gui.status.clear()
        self.gui.status.insertPlainText(message + "\n")
        self.app.processEvents()
