#version 330 core

in vec3 FragPos;

uniform float time;
uniform vec3 moonDir;

out vec4 FragColor;

float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

void main() {
    vec3 dir = normalize(FragPos);

    // Night sky gradient
    float horizon = smoothstep(-0.1, 0.3, dir.y);
    vec3 nightTop = vec3(0.005, 0.01, 0.04);
    vec3 nightMid = vec3(0.01, 0.015, 0.05);
    vec3 horizonColor = vec3(0.02, 0.03, 0.06);
    vec3 skyColor = mix(horizonColor, mix(nightMid, nightTop, horizon), horizon);

    // === Stars layer 1 ===
    vec3 starDir = dir * 200.0;
    vec2 starGrid = floor(starDir.xz / (1.0 + abs(dir.y) * 0.5));
    float starHash = hash(starGrid);
    if (starHash > 0.985 && dir.y > 0.05) {
        float twinkle = 0.6 + 0.4 * sin(time * (2.0 + starHash * 5.0) + starHash * 100.0);
        float brightness = (starHash - 0.985) / 0.015 * twinkle;
        vec3 starColor;
        if (starHash > 0.997)      starColor = vec3(1.0, 0.85, 0.6);
        else if (starHash > 0.993) starColor = vec3(0.7, 0.8, 1.0);
        else                        starColor = vec3(0.9, 0.9, 1.0);
        skyColor += starColor * brightness * 0.8;
    }

    // === Stars layer 2 ===
    vec2 starGrid2 = floor(starDir.xz * 1.7);
    float starHash2 = hash(starGrid2 + vec2(77.0, 33.0));
    if (starHash2 > 0.99 && dir.y > 0.1) {
        float twinkle2 = 0.5 + 0.5 * sin(time * 3.0 + starHash2 * 200.0);
        float brightness2 = (starHash2 - 0.99) / 0.01 * twinkle2 * 0.4;
        skyColor += vec3(0.8, 0.85, 1.0) * brightness2;
    }

    // ============================================
    // MOUNT FUJI — Due North (aligned with camp-lake-fuji axis)
    // ============================================
    vec2 viewH = normalize(dir.xz);
    vec2 fujiH = vec2(0.0, -1.0); // Due north = negative Z

    float hAngle = acos(clamp(dot(viewH, fujiH), -1.0, 1.0));

    float fujiWidth = 0.30;     // Angular half-width (~17 degrees)
    float fujiPeak = 0.40;      // Peak height in sky coordinates

    if (hAngle < fujiWidth * 1.3 && dir.y > -0.03 && dir.y < fujiPeak + 0.05) {
        float t = hAngle / fujiWidth; // 0 = center, 1 = base edge

        // Main cone — concave volcanic profile
        float mainCone = fujiPeak * pow(max(1.0 - t, 0.0), 0.55);

        // Gentle foothills extending beyond cone base
        float foothills = 0.08 * pow(max(1.0 - t * 0.75, 0.0), 2.0);

        // Slight asymmetry (real Fuji has Hoei crater on south-side)
        float asymSign = sign(dir.x); // left vs right side
        float asymmetry = 0.012 * asymSign * (1.0 - t);

        float mountainTop = max(mainCone, foothills) + asymmetry;

        // Ridge bumps along the profile
        float ridgeBump = sin(hAngle * 40.0) * 0.005 * (1.0 - t * t);
        mountainTop += ridgeBump;

        if (dir.y < mountainTop && dir.y > -0.02) {
            float heightRatio = dir.y / fujiPeak;
            vec3 mountainColor;

            // Snow line — upper ~40% of the mountain
            float snowLine = 0.50 * (1.0 - t * 0.15);

            if (heightRatio > snowLine) {
                // === Snow cap ===
                float snowT = (heightRatio - snowLine) / (1.0 - snowLine);
                snowT = clamp(snowT, 0.0, 1.0);

                vec3 baseSnow = vec3(0.35, 0.40, 0.55);
                vec3 peakSnow = vec3(0.75, 0.80, 0.90);
                mountainColor = mix(baseSnow, peakSnow, snowT * snowT);

                // Moonlight illumination on snow
                float moonFactor = max(dot(normalize(moonDir), vec3(0.0, 0.6, -0.8)), 0.0);
                mountainColor += vec3(0.12, 0.13, 0.18) * moonFactor * (0.5 + 0.5 * snowT);

                // Snow ridge detail — lighter streaks
                float snowRidge = sin(hAngle * 80.0 + dir.y * 30.0) * 0.025;
                mountainColor += vec3(snowRidge) * (1.0 - snowT * 0.5);

                // Gully shadows between snow ridges
                float gully = pow(sin(hAngle * 25.0 + 0.3) * 0.5 + 0.5, 3.0) * 0.04;
                mountainColor -= vec3(gully) * (1.0 - snowT);

            } else if (heightRatio > 0.12) {
                // === Rocky slopes ===
                float rockT = (heightRatio - 0.12) / (snowLine - 0.12);
                vec3 darkRock = vec3(0.035, 0.04, 0.065);
                vec3 midRock = vec3(0.07, 0.075, 0.11);
                mountainColor = mix(darkRock, midRock, rockT);

                // Rock texture detail
                float rockNoise = hash(floor(vec2(hAngle, dir.y) * 300.0)) * 0.015;
                mountainColor += vec3(rockNoise);

                // Slight vegetation patches on lower rock
                if (rockT < 0.3) {
                    float vegPatch = hash(floor(vec2(hAngle * 50.0, dir.y * 50.0))) * 0.01;
                    mountainColor.g += vegPatch;
                }
            } else {
                // === Forested base ===
                vec3 forestDark = vec3(0.02, 0.035, 0.04);
                vec3 forestLight = vec3(0.03, 0.05, 0.05);
                float forestT = max(heightRatio / 0.12, 0.0);
                mountainColor = mix(forestDark, forestLight, forestT);

                // Tree-like texture
                float treeTex = hash(floor(vec2(hAngle * 80.0, dir.y * 80.0))) * 0.008;
                mountainColor.g += treeTex;
            }

            // Edge softening — smooth silhouette
            float edgeSoft = smoothstep(0.0, 0.012, mountainTop - dir.y);

            // Atmospheric haze at base — mountain fades into sky near horizon
            float hazeT = smoothstep(-0.01, 0.12, dir.y);
            float hazeFade = hazeT * 0.85 + 0.15;

            skyColor = mix(skyColor, mountainColor, edgeSoft * hazeFade);
        }
    }

    // === Moon ===
    vec3 moonDirection = normalize(moonDir);
    float moonAngle = dot(dir, moonDirection);

    float moonDisc = smoothstep(0.997, 0.9985, moonAngle);
    vec3 moonFaceColor = vec3(0.98, 0.96, 0.9);
    vec2 moonUV = dir.xz / max(dir.y, 0.001);
    float crater = hash(floor(moonUV * 5.0)) * 0.15;
    moonFaceColor -= vec3(crater * 0.5, crater * 0.4, crater * 0.3) * moonDisc;
    skyColor += moonFaceColor * moonDisc * 3.0;

    float moonGlow = smoothstep(0.94, 0.998, moonAngle);
    skyColor += vec3(0.2, 0.25, 0.4) * moonGlow * (1.0 - moonDisc);

    float outerGlow = smoothstep(0.93, 0.98, moonAngle);
    skyColor += vec3(0.04, 0.04, 0.07) * outerGlow * (1.0 - moonGlow);

    // === Milky Way ===
    float milkyWay = smoothstep(0.8, 1.0, abs(dir.x * 0.5 + dir.y * 0.866));
    milkyWay *= smoothstep(0.0, 0.3, dir.y);
    float milkyNoise = hash(floor(starDir.xz * 0.3)) * 0.3;
    skyColor += vec3(0.02, 0.02, 0.04) * milkyWay * (0.5 + milkyNoise);

    FragColor = vec4(skyColor, 1.0);
}
