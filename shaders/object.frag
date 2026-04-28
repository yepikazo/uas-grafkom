#version 330 core

in vec3 FragPos;
in vec3 Normal;
in vec3 VertexColor;

uniform vec3 firePos;
uniform vec3 fireColor;
uniform float fireIntensity;
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

    // Campfire light
    float dist = length(firePos - FragPos);
    float attenuation = fireIntensity / (1.0 + 0.03 * dist + 0.005 * dist * dist);
    float fireDiff = max(dot(norm, normalize(firePos - FragPos)), 0.0);
    vec3 fireLighting = fireColor * fireDiff * attenuation * VertexColor;

    // Flicker
    float flicker = 0.88 + 0.12 * sin(time * 9.0 + FragPos.y * 3.0);
    fireLighting *= flicker;

    vec3 result = ambient + moonLighting + fireLighting;

    // Fog
    float fogDist = length(FragPos);
    float fogFactor = 1.0 - exp(-fogDist * 0.003);
    vec3 fogColor = vec3(0.02, 0.03, 0.06);
    result = mix(result, fogColor, fogFactor);

    FragColor = vec4(result, 1.0);
}
