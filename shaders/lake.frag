#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;

uniform vec3 viewPos;
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
    vec3 viewDir = normalize(viewPos - FragPos);

    // Deep blue-green night water color
    vec3 deepColor = vec3(0.01, 0.04, 0.08);
    vec3 shallowColor = vec3(0.02, 0.06, 0.12);

    // Fresnel effect for water surface
    float fresnel = pow(1.0 - max(dot(norm, viewDir), 0.0), 3.0);
    vec3 waterColor = mix(deepColor, shallowColor, fresnel);

    // Moon reflection on water
    vec3 moonReflectDir = reflect(-normalize(moonDir), norm);
    float moonSpec = pow(max(dot(viewDir, moonReflectDir), 0.0), 64.0);
    vec3 moonReflection = moonColor * moonSpec * 1.5;

    // Moon diffuse on water
    float moonDiff = max(dot(norm, normalize(moonDir)), 0.0);
    vec3 moonDiffuse = moonColor * moonDiff * 1.0;

    // Campfire reflections on water
    vec3 fireReflection = vec3(0.0);
    for (int i = 0; i < MAX_FIRES; i++) {
        if (i >= fireCount) {
            break;
        }

        vec3 toFire = firePositions[i] - FragPos;
        float dist = length(toFire);
        float attenuation = fireIntensities[i] / (1.0 + 0.02 * dist + 0.003 * dist * dist);
        vec3 fireReflectDir = reflect(-normalize(toFire), norm);
        float fireSpec = pow(max(dot(viewDir, fireReflectDir), 0.0), 16.0);
        float flicker = 0.85 + 0.15 * sin(time * 7.0 + FragPos.x * 3.0 + float(i) * 1.7);
        fireReflection += fireColors[i] * fireSpec * attenuation * 0.8 * flicker;
    }

    // Subtle sparkle effect
    float sparkle = pow(sin(FragPos.x * 20.0 + time * 2.0) *
                       sin(FragPos.z * 20.0 + time * 1.5), 8.0) * 0.3;
    vec3 sparkleColor = moonColor * sparkle * fresnel;

    // Combine
    vec3 ambient = vec3(0.04, 0.05, 0.1);
    vec3 result = waterColor + ambient + moonReflection + moonDiffuse + fireReflection + sparkleColor;

    // Night fog
    float fogDist = length(FragPos);
    float fogFactor = 1.0 - exp(-fogDist * 0.003);
    vec3 fogColor = vec3(0.02, 0.03, 0.06);
    result = mix(result, fogColor, fogFactor);

    FragColor = vec4(result, 0.85);
}
