#version 430

in vec2 vUV;

layout (location = 0) out vec4 FragColor;

layout (std430, binding = 1) buffer sbSpectrum {
	float bSpectrum[];
};

uniform vec2 uWinSize;

uniform float uFreqExp=0.5, uHueExp=1.5, uIntensityExp=2.0, uYExp=1.5;
uniform float uTopVal=0.0, uRange=5.0;
uniform float uMinClip=-100, uMaxClip=100;
uniform float uLowEnd=0.03, uHighEnd=0.75;

float unmap_x(float x) {
	return pow(2.0, pow(x, 1.0/uFreqExp)) - 1.0;
}

vec3 map_col(float x, float intensity) {
	return vec3(
		0.66 * pow(x, uHueExp),
		1.0,
		pow(intensity, uIntensityExp)
	);
}

vec3 hsv2rgb(vec3 c)
{
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
}


void main(void) {
	vec2 zoc = vUV;
	int sampidx = clamp(int(trunc(unmap_x(mix(uLowEnd, uHighEnd, zoc.x)) * bSpectrum.length())), 0, bSpectrum.length() - 1);
	float samp = bSpectrum[sampidx];
	samp = clamp(log(samp)/log(10), uMinClip, uMaxClip);
	float crity = pow(clamp((samp / uRange) - uTopVal + 1.0, 0.0, 1.0), uYExp);
	FragColor = zoc.y > crity ? vec4(0.0, 0.0, 0.0, 0.0) : vec4(hsv2rgb(map_col(zoc.x, crity)), crity);
	//FragColor = vec4(zoc, 0.0, 1.0);
	//FragColor = vec4(sampidx / float(bSpectrum.length()), 0.0, 0.0, 1.0);
}
