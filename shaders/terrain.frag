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
    // Height-based color blending for terrain
    vec3 grassColor = vec3(0.08, 0.18, 0.06);      // Dark grass (night)
    vec3 dirtColor = vec3(0.12, 0.08, 0.05);        // Dark dirt
    vec3 rockColor = vec3(0.15, 0.14, 0.13);        // Dark rock
    vec3 snowColor = vec3(0.5, 0.55, 0.65);         // Moonlit snow
    vec3 sandColor = vec3(0.18, 0.15, 0.08);        // Dark sand (near lake)

    // Blend based on height
    vec3 baseColor;
    if (Height < 0.1) {
        baseColor = sandColor;
    } else if (Height < 0.5) {
        float t = smoothstep(0.1, 0.5, Height);
        baseColor = mix(sandColor, grassColor, t);
    } else if (Height < 2.0) {
        float t = smoothstep(0.5, 2.0, Height);
        baseColor = mix(grassColor, dirtColor, t);
    } else if (Height < 4.0) {
        float t = smoothstep(2.0, 4.0, Height);
        baseColor = mix(dirtColor, rockColor, t);
    } else {
        float t = smoothstep(4.0, 6.0, Height);
        baseColor = mix(rockColor, snowColor, t);
    }

    vec3 norm = normalize(Normal);

    // Moonlight (directional)
    float moonDiff = max(dot(norm, normalize(moonDir)), 0.0);
    vec3 moonLighting = moonColor * moonDiff * 0.3;

    // Ambient light (night sky)
    vec3 ambient = vec3(0.03, 0.04, 0.08);

    // Campfire point light
    float dist = length(firePos - FragPos);
    float attenuation = fireIntensity / (1.0 + 0.15 * dist + 0.08 * dist * dist);
    float fireDiff = max(dot(norm, normalize(firePos - FragPos)), 0.0);
    vec3 fireLighting = fireColor * fireDiff * attenuation;

    // Flickering effect
    float flicker = 0.9 + 0.1 * sin(time * 8.0 + FragPos.x * 2.0);
    fireLighting *= flicker;

    vec3 result = baseColor * (ambient + moonLighting + fireLighting);

    // Add slight fog for depth
    float fogDist = length(FragPos);
    float fogFactor = 1.0 - exp(-fogDist * 0.015);
    vec3 fogColor = vec3(0.02, 0.03, 0.06);
    result = mix(result, fogColor, fogFactor);

    FragColor = vec4(result, 1.0);
}
