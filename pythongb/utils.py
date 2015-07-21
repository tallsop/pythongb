def set_bit(self, v, index, x):
        """Set the index:th bit of v to x, and return the new value."""
        mask = 1 << index
        v &= ~mask

        if x:
            v |= mask

        return v