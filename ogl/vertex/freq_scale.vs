#version 430

in vec2 vPosition;
in vec2 vTexCoord;

out vec2 vUV;

uniform float uSampIdx=0.003;
uniform float uLow=-3.0, uHigh=0.0;
uniform float uMinFactor=0.8, uMaxFactor=1.0;
uniform vec2 uCenter;

layout (std430, binding = 1) buffer sbSpectrum {
	float bSpectrum[];
};

void main(void) {
	float scsamp = uSampIdx * bSpectrum.length();
	int lowidx = clamp(int(floor(scsamp)), 0, bSpectrum.length() - 1);
	int highidx = clamp(int(ceil(scsamp)), 0, bSpectrum.length() - 1);
	float lsamp = log(bSpectrum[lowidx]) / log(10);
	float hsamp = log(bSpectrum[highidx]) / log(10);
	float normu = mix(lsamp, hsamp, scsamp - floor(scsamp));
	normu = clamp((normu - uLow) / (uHigh - uLow), 0.0, 1.0);
	float factor = mix(uMinFactor, uMaxFactor, normu);
	gl_Position = vec4(uCenter + factor * (vPosition - uCenter), 0.0, 1.0);
	vUV = vTexCoord;
	gl_PointSize = 1.0;
}
