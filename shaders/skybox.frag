#version 330 core

in vec3 FragPos;

uniform float time;
uniform vec3 moonDir;

out vec4 FragColor;

// Hash function for procedural stars
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

void main() {
    vec3 dir = normalize(FragPos);

    // Night sky gradient
    float horizon = smoothstep(-0.1, 0.3, dir.y);
    vec3 nightTop = vec3(0.005, 0.01, 0.04);       // Deep dark blue
    vec3 nightMid = vec3(0.01, 0.015, 0.05);       // Slightly lighter
    vec3 horizonColor = vec3(0.02, 0.03, 0.06);    // Horizon glow

    vec3 skyColor = mix(horizonColor, mix(nightMid, nightTop, horizon), horizon);

    // Stars
    vec3 starDir = dir * 200.0;
    vec2 starGrid = floor(starDir.xz / (1.0 + abs(dir.y) * 0.5));
    float starHash = hash(starGrid);

    if (starHash > 0.985 && dir.y > 0.05) {
        float twinkle = 0.6 + 0.4 * sin(time * (2.0 + starHash * 5.0) + starHash * 100.0);
        float brightness = (starHash - 0.985) / 0.015;
        brightness *= twinkle;

        // Star color variety
        vec3 starColor;
        if (starHash > 0.997) {
            starColor = vec3(1.0, 0.85, 0.6);  // Warm yellow star
        } else if (starHash > 0.993) {
            starColor = vec3(0.7, 0.8, 1.0);   // Blue-white star
        } else {
            starColor = vec3(0.9, 0.9, 1.0);   // White star
        }

        skyColor += starColor * brightness * 0.8;
    }

    // Additional star layer (smaller/dimmer)
    vec2 starGrid2 = floor(starDir.xz * 1.7);
    float starHash2 = hash(starGrid2 + vec2(77.0, 33.0));
    if (starHash2 > 0.99 && dir.y > 0.1) {
        float twinkle2 = 0.5 + 0.5 * sin(time * 3.0 + starHash2 * 200.0);
        float brightness2 = (starHash2 - 0.99) / 0.01 * twinkle2 * 0.4;
        skyColor += vec3(0.8, 0.85, 1.0) * brightness2;
    }

    // Moon
    vec3 moonDirection = normalize(moonDir);
    float moonAngle = dot(dir, moonDirection);

    // Moon disc
    float moonDisc = smoothstep(0.9985, 0.9995, moonAngle);

    // Moon color with slight gradient
    vec3 moonFaceColor = vec3(0.95, 0.92, 0.8);
    // Add some "craters" using hash
    vec2 moonUV = dir.xz / max(dir.y, 0.001);
    float crater = hash(floor(moonUV * 5.0)) * 0.15;
    moonFaceColor -= vec3(crater * 0.5, crater * 0.4, crater * 0.3) * moonDisc;

    skyColor += moonFaceColor * moonDisc * 2.0;

    // Moon glow/halo
    float moonGlow = smoothstep(0.97, 0.999, moonAngle);
    skyColor += vec3(0.15, 0.15, 0.2) * moonGlow * (1.0 - moonDisc);

    // Outer halo
    float outerGlow = smoothstep(0.93, 0.98, moonAngle);
    skyColor += vec3(0.04, 0.04, 0.07) * outerGlow * (1.0 - moonGlow);

    // Milky way band (subtle)
    float milkyWay = smoothstep(0.8, 1.0, abs(dir.x * 0.5 + dir.y * 0.866));
    milkyWay *= smoothstep(0.0, 0.3, dir.y);
    float milkyNoise = hash(floor(starDir.xz * 0.3)) * 0.3;
    skyColor += vec3(0.02, 0.02, 0.04) * milkyWay * (0.5 + milkyNoise);

    FragColor = vec4(skyColor, 1.0);
}
