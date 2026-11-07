#pragma once
struct TwoWire { bool begin(int = -1, int = -1) { return true; } };
extern TwoWire Wire;
