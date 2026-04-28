#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;
in float Height;

uniform vec3 firePos;
uniform vec3 fireColor;
uniform float fireIntensity;
uniform vec3 moonDir;
uniform vec3 moonColor;
uniform float time;

out vec4 FragColor;

void main() {
    // Height-based color blending for large Motosu terrain
    vec3 sandColor = vec3(0.18, 0.15, 0.08);
    vec3 grassColor = vec3(0.08, 0.18, 0.06);
    vec3 dirtColor = vec3(0.12, 0.08, 0.05);
    vec3 rockColor = vec3(0.15, 0.14, 0.13);
    vec3 snowColor = vec3(0.5, 0.55, 0.65);

    vec3 baseColor;
    if (Height < 0.3) {
        baseColor = sandColor;
    } else if (Height < 3.0) {
        float t = smoothstep(0.3, 3.0, Height);
        baseColor = mix(sandColor, grassColor, t);
    } else if (Height < 8.0) {
        float t = smoothstep(3.0, 8.0, Height);
        baseColor = mix(grassColor, dirtColor, t);
    } else if (Height < 15.0) {
        float t = smoothstep(8.0, 15.0, Height);
        baseColor = mix(dirtColor, rockColor, t);
    } else {
        float t = smoothstep(15.0, 22.0, Height);
        baseColor = mix(rockColor, snowColor, t);
    }

    vec3 norm = normalize(Normal);

    // Moonlight (directional)
    float moonDiff = max(dot(norm, normalize(moonDir)), 0.0);
    vec3 moonLighting = moonColor * moonDiff * 0.8;

    // Ambient light (night sky)
    vec3 ambient = vec3(0.08, 0.1, 0.18);

    // Campfire point light
    float dist = length(firePos - FragPos);
    float attenuation = fireIntensity / (1.0 + 0.03 * dist + 0.005 * dist * dist);
    float fireDiff = max(dot(norm, normalize(firePos - FragPos)), 0.0);
    vec3 fireLighting = fireColor * fireDiff * attenuation;

    // Flickering effect
    float flicker = 0.9 + 0.1 * sin(time * 8.0 + FragPos.x * 2.0);
    fireLighting *= flicker;

    vec3 result = baseColor * (ambient + moonLighting + fireLighting);

    // Distance fog adjusted for large terrain
    float fogDist = length(FragPos);
    float fogFactor = 1.0 - exp(-fogDist * 0.003);
    vec3 fogColor = vec3(0.02, 0.03, 0.06);
    result = mix(result, fogColor, fogFactor);

    FragColor = vec4(result, 1.0);
}
