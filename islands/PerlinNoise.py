import numpy as np

# Hash lookup table as defined by Ken Perlin.  This is a randomly arranged array of all numbers from 0-255 inclusive.
permutation = [151, 160, 137, 91, 90, 15,
               131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23,
               190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33,
               88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134, 139, 48, 27, 166,
               77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244,
               102, 143, 54, 65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196,
               135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226, 250, 124, 123,
               5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42,
               223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9,
               129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228,
               251, 34, 242, 193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14, 239, 107,
               49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254,
               138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180]

a_permutation = np.array(permutation, dtype=np.uint8)


class AcceleratedPerlin:
    p = []

    def __init__(self):
        for x in range(512):
            self.p.append(a_permutation[x % 256])

        self.p = np.array(self.p, dtype=np.uint8)

    def octavePerlin(self, coordinates, octaves, persistance):
        total = 0
        frequency = 1
        amplitude = 1
        maxValue = 0
        for i in range(octaves):
            total += self.perlin(coordinates * frequency) * amplitude

            maxValue += amplitude
            amplitude *= persistance
            frequency *= 2

        return total / maxValue

    def perlin(self, coordinates):

        int_coords = coordinates.astype(np.int32)
        xi = int_coords[:, :, :, 0]
        yi = int_coords[:, :, :, 1]
        zi = int_coords[:, :, :, 2]

        xf = np.remainder(coordinates[:, :, :, 0], 1)
        yf = np.remainder(coordinates[:, :, :, 1], 1)
        zf = np.remainder(coordinates[:, :, :, 2], 1)

        u = self.fade(xf)
        v = self.fade(yf)
        w = self.fade(zf)

        aaa = self.p[self.p[self.p[xi] + yi] + zi]
        aba = self.p[self.p[self.p[xi] + self.inc(yi)] + zi]
        aab = self.p[self.p[self.p[xi] + yi] + self.inc(zi)]
        abb = self.p[self.p[self.p[xi] + self.inc(yi)] + self.inc(zi)]
        baa = self.p[self.p[self.p[self.inc(xi)] + yi] + zi]
        bba = self.p[self.p[self.p[self.inc(xi)] + self.inc(yi)] + zi]
        bab = self.p[self.p[self.p[self.inc(xi)] + yi] + self.inc(zi)]
        bbb = self.p[self.p[self.p[self.inc(xi)] + self.inc(yi)] + self.inc(zi)]

        x1 = self.lerp(self.grad(aaa, xf, yf, zf), self.grad(baa, xf - 1, yf, zf), u)
        x2 = self.lerp(self.grad(aba, xf, yf - 1, zf), self.grad(bba, xf - 1, yf - 1, zf), u)
        y1 = self.lerp(x1, x2, v)
        x1 = self.lerp(self.grad(aab, xf, yf, zf - 1), self.grad(bab, xf - 1, yf, zf - 1), u)
        x2 = self.lerp(self.grad(abb, xf, yf - 1, zf - 1), self.grad(bbb, xf - 1, yf - 1, zf - 1), u)
        y2 = self.lerp(x1, x2, v)

        return (self.lerp(y1, y2, w) + 1) / 2

    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def inc(self, num):
        return num + 1

    def grad(self, hash, x, y, z):
        hash = hash & 15

        output_array = np.empty(x.shape, dtype=np.float32)

        output_array = np.where(hash == 0, x + y, output_array)
        output_array = np.where(hash == 1, -x + y, output_array)
        output_array = np.where(hash == 2, x - y, output_array)
        output_array = np.where(hash == 3, -x - y, output_array)

        output_array = np.where(hash == 4, x + z, output_array)
        output_array = np.where(hash == 5, -x + z, output_array)
        output_array = np.where(hash == 6, x - z, output_array)
        output_array = np.where(hash == 7, -x - z, output_array)

        output_array = np.where(hash == 8, y + z, output_array)
        output_array = np.where(hash == 9, -y + z, output_array)
        output_array = np.where(hash == 10, y - z, output_array)
        output_array = np.where(hash == 11, -y - z, output_array)

        output_array = np.where(hash == 12, y + x, output_array)
        output_array = np.where(hash == 13, -y + z, output_array)
        output_array = np.where(hash == 14, y - x, output_array)
        output_array = np.where(hash == 15, -y - z, output_array)

        return output_array

    # linear interpolate
    def lerp(self, a, b, x):
        return a + x * (b - a)
