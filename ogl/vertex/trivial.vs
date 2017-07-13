#version 330

in vec2 vPosition;
//attribute vec2 vTexCoord;

//varying vec2 vUV;

void main(void) {
	gl_Position = vec4(vPosition, 0.0, 1.0);
	/*
	vUV = vTexCoord;
	gl_PointSize = 1.0;
	*/
}
