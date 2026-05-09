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
    vec3 lightDir = normalize(moonDir);
    
    // Warna dasar air (gelap untuk kontras)
    vec3 deepColor = vec3(0.002, 0.005, 0.02);
    vec3 shallowColor = vec3(0.015, 0.04, 0.08);
    float fresnel = pow(1.0 - max(dot(norm, viewDir), 0.0), 3.0);
    vec3 waterColorBase = mix(deepColor, shallowColor, fresnel);
    
    // Efek jarak ke api
    float minDist = 1000.0;
    for (int i = 0; i < MAX_FIRES; i++) {
        if (i >= fireCount) break;
        float dist = length(FragPos - firePositions[i]);
        minDist = min(minDist, dist);
    }
    
    float warmRadius = 7.0;
    float warmthFactor = 1.0 - smoothstep(0.0, warmRadius, minDist);
    warmthFactor = pow(warmthFactor, 2.5);
    vec3 warmColor = vec3(0.5, 0.22, 0.06);
    vec3 waterColor = waterColorBase + warmColor * warmthFactor * 0.7;
    
    float darkStart = warmRadius;
    float darkEnd = warmRadius + 10.0;
    float farDarken = 1.0 - smoothstep(darkStart, darkEnd, minDist);
    waterColor *= (0.3 + farDarken * 0.5);
    
    float glowRadius = 5.0;
    float glow = 1.0 - smoothstep(0.0, glowRadius, minDist);
    glow = pow(glow, 1.8) * 0.35;
    waterColor += vec3(0.45, 0.2, 0.05) * glow;
    
    // Diffuse bulan (ditingkatkan)
    float moonDiff = max(dot(norm, lightDir), 0.0);
    vec3 moonDiffuse = moonColor * moonDiff * 0.6;
    
    // Specular bulan (ditingkatkan)
    vec3 reflectDir = reflect(-lightDir, norm);
    float moonSpec = pow(max(dot(viewDir, reflectDir), 0.0), 256.0);
    vec3 moonReflection = moonColor * moonSpec * 3.0;
    
    // Pantulan api (ditingkatkan intensitasnya)
    vec3 fireReflection = vec3(0.0);
    for (int i = 0; i < MAX_FIRES; i++) {
        if (i >= fireCount) break;
        vec3 toFire = firePositions[i] - FragPos;
        float dist = length(toFire);
        float attenuation = fireIntensities[i] / (1.0 + 0.02 * dist + 0.003 * dist * dist);
        vec3 fireLightDir = normalize(toFire);
        vec3 reflectFire = reflect(-fireLightDir, norm);
        // Higher exponent (64) = smaller, sharper specular spot on water
        float fireSpec = pow(max(dot(viewDir, reflectFire), 0.0), 64.0);
        float flicker = 0.82 + 0.18 * sin(time * 7.0 + FragPos.x * 3.0 + float(i) * 1.7);
        fireReflection += fireColors[i] * fireSpec * attenuation * 0.5 * flicker;
    }
    
    // Ambient tetap gelap
    vec3 ambient = vec3(0.01, 0.02, 0.04);
    vec3 result = waterColor + ambient + moonReflection + moonDiffuse + fireReflection;
    
    // Kabut
    float fogDist = length(FragPos);
    float fogFactor = 1.0 - exp(-fogDist * 0.003);
    vec3 fogColor = vec3(0.005, 0.01, 0.02);
    result = mix(result, fogColor, fogFactor);
    
    FragColor = vec4(result, 0.85);
}