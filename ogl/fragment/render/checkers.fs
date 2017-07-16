#version 330

//varying vec2 vUV;

layout (location = 0) out vec4 FragColor;

uniform vec2 uWinSize;

uniform int uCheckers = 8;

void main(void) {
	vec2 zoc = gl_FragCoord.xy / uWinSize;
	int mhd = int(floor(uCheckers * zoc.x) + floor(uCheckers * zoc.y));
	int edge = int(max(ceil(uCheckers * zoc.x), ceil(uCheckers * zoc.y)));
	FragColor = vec4(
		mhd % 2 == 0 ? 1.0 : 0.0,
		edge == uCheckers ? 1.0 : 0.0,
		mhd % 2 == 0 ? 1.0 : 0.0,
		1.0
	);
}
