#version 430

in vec2 vUV;

layout (location = 0) out vec4 FragColor;

uniform vec4 uColor = vec4(1.0, 1.0, 1.0, 1.0);
uniform sampler2D uTex;

void main(void) {
	FragColor = texture(uTex, vUV) * uColor;
}
