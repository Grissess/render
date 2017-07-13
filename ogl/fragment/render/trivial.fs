#version 330

#define CHECKERS 8

//varying vec2 vUV;

layout (location = 0) out vec4 FragColor;

uniform vec2 uWinSize;

void main(void) {
	vec2 zoc = gl_FragCoord.xy / uWinSize;
	int mhd = int(floor(CHECKERS * zoc.x) + floor(CHECKERS * zoc.y));
	int edge = int(max(ceil(CHECKERS * zoc.x), ceil(CHECKERS * zoc.y)));
	FragColor = vec4(
		mhd % 2 == 0 ? 1.0 : 0.0,
		edge == CHECKERS ? 1.0 : 0.0,
		mhd % 2 == 0 ? 1.0 : 0.0,
		1.0
	);
}
