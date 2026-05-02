#version 330 core

in vec3 FragPos;

uniform float time;
uniform vec3 moonDir;

out vec4 FragColor;

// ---- Hash / noise ----
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float vnoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i + vec2(0.0,0.0)), hash(i + vec2(1.0,0.0)), u.x),
               mix(hash(i + vec2(0.0,1.0)), hash(i + vec2(1.0,1.0)), u.x), u.y);
}

// ---- Fuji silhouette: flat/blunt summit (crater) + smooth cone ----
// t = 0 (centre peak) .. 1 (base edge)
float fujProfile(float t) {
    float peakH    = 0.28;
    float flatZone = 0.09;  // flat crater plateau at summit

    float coneT = clamp((t - flatZone) / (1.0 - flatZone), 0.0, 1.0);
    float cone  = peakH * pow(1.0 - coneT, 0.80);
    float skirt = 0.048 * pow(clamp(1.0 - t * 0.63, 0.0, 1.0), 3.5);
    return t < flatZone ? peakH : max(cone, skirt);
}

void main() {
    vec3 dir = normalize(FragPos);

    // ---- Night sky gradient ----
    float horizon = smoothstep(-0.08, 0.25, dir.y);
    vec3 nightTop     = vec3(0.01, 0.02, 0.09);
    vec3 nightMid     = vec3(0.02, 0.03, 0.11);
    vec3 horizonColor = vec3(0.04, 0.05, 0.13);
    vec3 skyColor = mix(horizonColor, mix(nightMid, nightTop, horizon), horizon);

    // ---- Stars layer 1 ----
    vec3 starDir = dir * 200.0;
    vec2 starGrid = floor(starDir.xz / (1.0 + abs(dir.y) * 0.5));
    float starHash = hash(starGrid);
    if (starHash > 0.985 && dir.y > 0.05) {
        float twinkle = 0.6 + 0.4 * sin(time * (2.0 + starHash * 5.0) + starHash * 100.0);
        float brightness = (starHash - 0.985) / 0.015 * twinkle;
        vec3 starColor;
        if      (starHash > 0.997) starColor = vec3(1.0, 0.85, 0.6);
        else if (starHash > 0.993) starColor = vec3(0.7, 0.8,  1.0);
        else                        starColor = vec3(0.9, 0.9,  1.0);
        skyColor += starColor * brightness * 0.8;
    }

    // ---- Stars layer 2 ----
    vec2 starGrid2  = floor(starDir.xz * 1.7);
    float starHash2 = hash(starGrid2 + vec2(77.0, 33.0));
    if (starHash2 > 0.99 && dir.y > 0.1) {
        float twinkle2   = 0.5 + 0.5 * sin(time * 3.0 + starHash2 * 200.0);
        float brightness2 = (starHash2 - 0.99) / 0.01 * twinkle2 * 0.4;
        skyColor += vec3(0.8, 0.85, 1.0) * brightness2;
    }

    // ================================================================
    //  MOUNT FUJI — Due North (−Z)
    // ================================================================
    vec2  dirXZ    = dir.xz;
    float horizLen = length(dirXZ);

    if (horizLen > 0.001) {
        vec2 viewH = dirXZ / horizLen;
        vec2 fujiH = vec2(0.0, -1.0);   // due north = −Z

        float hAngle        = acos(clamp(dot(viewH, fujiH), -1.0, 1.0));
        float fujiHalfWidth = 0.28;

        if (hAngle < fujiHalfWidth) {
            float t = hAngle / fujiHalfWidth;

            float mountainTop = fujProfile(t);

            // Subtle ridge noise on silhouette
            mountainTop += vnoise(vec2(hAngle * 55.0, 1.0)) * 0.004 * (1.0 - t * t);

            // Faint Hoei-crater asymmetry
            mountainTop -= smoothstep(0.0, 0.4, -dir.x) * 0.010 * smoothstep(0.8, 0.3, t);

            if (dir.y < mountainTop) {

                float moonFactor = max(dot(normalize(moonDir), vec3(0.0, 0.6, -0.8)), 0.0);

                // ============================================================
                //  SNOW CAP — determined by ABSOLUTE height (dir.y), not ratio
                //  This naturally makes only the central top covered in snow;
                //  the lower sloped sides fall below the snow line → bare rock.
                // ============================================================
                //  Mountain peak  : dir.y ≈ 0.28
                //  Snow starts at : dir.y ≈ 0.19  (top ~1/3 in absolute height)
                //  Below 0.19     : always bare volcanic rock
                float snowAbs = 0.19;

                // Slight irregular boundary (avoids a perfectly horizontal cut)
                float snowVar  = vnoise(vec2(hAngle * 9.0, 0.42)) * 0.016;
                float snowMask = smoothstep(snowAbs - 0.028, snowAbs + 0.028, dir.y + snowVar);

                // ---- Rock colour (simplified — dark volcanic blue-grey) ----
                vec3 rockColor = vec3(0.030, 0.034, 0.060);
                float rockN    = vnoise(vec2(hAngle * 140.0, dir.y * 140.0)) * 0.008;
                rockColor += vec3(rockN * 0.5, rockN * 0.4, rockN);

                // Slightly lighter near tree-line for visual depth
                float treeT = smoothstep(0.0, 0.06, dir.y);
                rockColor   = mix(vec3(0.015, 0.022, 0.026), rockColor, treeT);

                // ---- Snow colour (moonlit cap, cold blue-white) ----
                // Gradient: blue-lavender at snow edge → cold silver-white at peak
                float snowHT  = clamp((dir.y - snowAbs) / (0.28 - snowAbs), 0.0, 1.0);
                vec3 snowEdge = mix(vec3(0.20, 0.25, 0.40), vec3(0.55, 0.63, 0.80), moonFactor * 0.85);
                vec3 snowPeak = vec3(0.76, 0.81, 0.93);
                vec3 snowColor = mix(snowEdge, snowPeak, snowHT * snowHT);

                // Fine snow texture (avalanche streaks)
                float snowDtl = vnoise(vec2(hAngle * 38.0, dir.y * 11.0)) * 0.016;
                snowColor += vec3(snowDtl);

                // Combine rock + snow
                vec3 mountainColor = mix(rockColor, snowColor, snowMask);

                // ---- Moonlit rim glow on silhouette edge ----
                float rimGlow = smoothstep(0.014, 0.0, mountainTop - dir.y);
                mountainColor += vec3(0.22, 0.30, 0.52) * moonFactor * rimGlow * 0.45;

                // ---- Blend into sky ----
                float edgeSoft    = smoothstep(0.0, 0.010, mountainTop - dir.y);
                float angularEdge = smoothstep(0.0, 0.04,  fujiHalfWidth - hAngle);
                float baseHaze    = smoothstep(-0.02, 0.10, dir.y);

                // Atmospheric haze fades mountain base into horizon
                float hazeBlend = smoothstep(0.10, 0.0, dir.y);
                mountainColor   = mix(mountainColor, horizonColor + vec3(0.01, 0.01, 0.03), hazeBlend * 0.45);

                skyColor = mix(skyColor, mountainColor, edgeSoft * angularEdge * baseHaze);
            }
        }
    }

    // ---- Moon ----
    vec3  moonDirection = normalize(moonDir);
    float moonAngle     = dot(dir, moonDirection);

    float moonDisc      = smoothstep(0.99905, 0.99955, moonAngle);
    vec3  moonFaceColor = vec3(0.98, 0.96, 0.9);
    vec2  moonUV  = dir.xz / max(dir.y, 0.001);
    float crater  = hash(floor(moonUV * 5.0)) * 0.15;
    moonFaceColor -= vec3(crater * 0.5, crater * 0.4, crater * 0.3) * moonDisc;
    skyColor += moonFaceColor * moonDisc * 3.2;

    float moonGlow  = smoothstep(0.975, 0.9995, moonAngle);
    skyColor += vec3(0.14, 0.18, 0.32) * moonGlow * (1.0 - moonDisc);

    float outerGlow = smoothstep(0.955, 0.988,  moonAngle);
    skyColor += vec3(0.025, 0.03, 0.055) * outerGlow * (1.0 - moonGlow);

    // ---- Milky Way ----
    float milkyWay   = smoothstep(0.8, 1.0, abs(dir.x * 0.5 + dir.y * 0.866));
    milkyWay        *= smoothstep(0.0, 0.3, dir.y);
    float milkyNoise = hash(floor(starDir.xz * 0.3)) * 0.3;
    skyColor += vec3(0.02, 0.02, 0.04) * milkyWay * (0.5 + milkyNoise);

    FragColor = vec4(skyColor, 1.0);
}
