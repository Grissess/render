#version 430

in vec2 vUV;

layout (location = 0) out vec4 FragColor;

uniform sampler2D uFB;
uniform float uPhaseOff;
uniform float uAngle = 0.0;
uniform float uFreq = 100.0;
uniform float uSampF = 0.003;
uniform float uLow = -3.0, uHigh = 0.0;
uniform float uMaxMag = 0.005, uMinMag = 0.0;
uniform vec4 uColor = vec4(1.0, 1.0, 1.0, 1.0);

layout (std430, binding = 1) buffer sbSpectrum {
	float bSpectrum[];
};

void main(void) {
	float scsamp = uSampF * bSpectrum.length();
	int lowidx = clamp(int(floor(scsamp)), 0, bSpectrum.length() - 1);
	int highidx = clamp(int(ceil(scsamp)), 0, bSpectrum.length() - 1);
	float lsamp = log(bSpectrum[lowidx]) / log(10);
	float hsamp = log(bSpectrum[highidx]) / log(10);
	float normu = mix(lsamp, hsamp, scsamp - floor(scsamp));
	normu = clamp((normu - uLow) / (uHigh - uLow), 0.0, 1.0);
	float amp = mix(uMinMag, uMaxMag, normu);
	mat2 rot = mat2(cos(uAngle), sin(uAngle), -sin(uAngle), cos(uAngle));
	FragColor = uColor * texture(uFB, vUV + rot * vec2(amp * sin(uFreq * vUV.y + uPhaseOff), 0));
}
