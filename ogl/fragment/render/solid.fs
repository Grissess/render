#version 430

layout (location = 0) out vec4 FragColor;

uniform vec4 uColor = vec4(1.0, 1.0, 1.0, 1.0);

void main(void) {
	FragColor = uColor;
}
