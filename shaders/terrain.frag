#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;
in float Height;

const int MAX_FIRES = 3;
uniform int fireCount;
uniform vec3 firePositions[MAX_FIRES];
uniform vec3 fireColors[MAX_FIRES];
uniform float fireIntensities[MAX_FIRES];
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
    vec3 ambient = vec3(0.15, 0.2, 0.25);

    // Campfire point lights
    vec3 fireLighting = vec3(0.0);
    for (int i = 0; i < MAX_FIRES; i++) {
        if (i >= fireCount) {
            break;
        }

        vec3 toFire = firePositions[i] - FragPos;
        float dist = length(toFire);
        float attenuation = fireIntensities[i] / (1.0 + 0.03 * dist + 0.005 * dist * dist);
        float fireDiff = max(dot(norm, normalize(toFire)), 0.0);
        float flicker = 0.9 + 0.1 * sin(time * 8.0 + FragPos.x * 2.0 + float(i) * 1.7);
        fireLighting += fireColors[i] * fireDiff * attenuation * flicker;
    }

    vec3 result = baseColor * (ambient + moonLighting + fireLighting);

    // Distance fog adjusted for large terrain
    float fogDist = length(FragPos);
    float fogFactor = 1.0 - exp(-fogDist * 0.003);
    vec3 fogColor = vec3(0.02, 0.03, 0.06);
    result = mix(result, fogColor, fogFactor);

    FragColor = vec4(result, 1.0);
}
