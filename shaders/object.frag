#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 VertexColor;

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
    vec3 norm = normalize(Normal);

    // Ambient (night)
    vec3 ambient = vec3(0.08, 0.1, 0.18) * VertexColor;

    // Moonlight
    float moonDiff = max(dot(norm, normalize(moonDir)), 0.0);
    vec3 moonLighting = moonColor * moonDiff * 1.4 * VertexColor;

    // Campfire lights
    vec3 fireLighting = vec3(0.0);
    for (int i = 0; i < MAX_FIRES; i++) {
        if (i >= fireCount) {
            break;
        }

        vec3 toFire = firePositions[i] - FragPos;
        float dist = length(toFire);
        float attenuation = fireIntensities[i] / (1.0 + 0.03 * dist + 0.005 * dist * dist);
        float fireDiff = max(dot(norm, normalize(toFire)), 0.0);
        float flicker = 0.88 + 0.12 * sin(time * 9.0 + FragPos.y * 3.0 + float(i) * 1.7);
        fireLighting += fireColors[i] * fireDiff * attenuation * VertexColor * flicker;
    }

    vec3 result = ambient + moonLighting + fireLighting;

    // Fog
    float fogDist = length(FragPos);
    float fogFactor = 1.0 - exp(-fogDist * 0.003);
    vec3 fogColor = vec3(0.02, 0.03, 0.06);
    result = mix(result, fogColor, fogFactor);

    FragColor = vec4(result, 1.0);
}
