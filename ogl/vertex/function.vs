#version 430

in float vX;
in float vY;

void main(void) {
	gl_Position = vec4(vX, vY, 0.0, 1.0);
	gl_PointSize = 1.0;
}
