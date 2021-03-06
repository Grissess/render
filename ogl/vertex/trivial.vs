#version 430

in vec2 vPosition;
in vec2 vTexCoord;

out vec2 vUV;

void main(void) {
	gl_Position = vec4(vPosition, 0.0, 1.0);
	vUV = vTexCoord;
	gl_PointSize = 1.0;
}
