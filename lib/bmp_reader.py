class BMPReader(object):
    def __init__(self, filename):
        self._filename = filename
        self._read_img_data()

    def get_pixels(self):
        """
        Returns a multi-dimensional array of the RGB values of each pixel in the
        image, arranged by rows and columns from the top-left.  Access any pixel
        by its location, eg:

        pixels = BMPReader(filename).get_pixels()
        top_left_px = pixels[0][0] # [255, 0, 0]
        bottom_right_px = pixels[8][8] # [0, 255, 255]
        """
        pixel_grid = []
        pixel_data = list(self._pixel_data) # So we're working on a copy

        # need this for row padding
        # https://en.wikipedia.org/wiki/BMP_file_format#Pixel_array_(bitmap_data)
        lineLength = self.width * 3
        if ((lineLength % 4) != 0):
            lineLength = (int(lineLength / 4) + 1) * 4
        padding = lineLength - self.width*3

        for y in range(self.height):
            row = []
            for i in range(padding):
                pixel_data.pop()
            for x in range(self.width):
                r = pixel_data.pop()
                g = pixel_data.pop()
                b = pixel_data.pop()
                row.append((r, g, b))
            pixel_grid.insert(0, row)
        pixel_grid.reverse()
        return pixel_grid
    
    def read_column_pixels(self, idx):
        idx-=1
        column_pixels=[]
        with open(self._filename, 'rb') as f:
            # Iterate over the image column by column
            for y in range(self.height - 1, -1, -1):
                # Calculate byte position of pixel in file
                byte_pos = 54 + (y * (self.width * 3 + self.row_padding)) + (idx * 3)

                # Read RGB values of pixel
                f.seek(byte_pos)
                b = int.from_bytes(f.read(1), 'little')
                g = int.from_bytes(f.read(1), 'little')
                r = int.from_bytes(f.read(1), 'little')
                column_pixels.append((r, g, b))

            return column_pixels

    def _read_img_data(self):
        def lebytes_to_int(bytes):
            n = 0x00
            while len(bytes) > 0:
                n <<= 8
                n |= bytes.pop()
            return int(n)

        with open(self._filename, 'rb') as f:
            img_bytes = list(bytearray(f.read(54)))

        # Before we proceed, we need to ensure certain conditions are met
        assert img_bytes[0:2] == [66, 77], "Not a valid BMP file"
        assert lebytes_to_int(img_bytes[30:34]) == 0, \
            "Compression is not supported"
        assert lebytes_to_int(img_bytes[28:30]) == 24, \
            "Only 24-bit colour depth is supported"

        self.width = lebytes_to_int(img_bytes[18:22])
        self.height = lebytes_to_int(img_bytes[22:26])
        # Calculate row padding and column size in bytes
        self.row_padding = (4 - (self.width * 3) % 4) % 4
