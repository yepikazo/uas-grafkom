#version 330 core

// Per-firefly data
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
layout(location = 2) in float aBrightness;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3  vColor;
out float vBrightness;

void main() {
    vColor      = aColor;
    vBrightness = aBrightness;

    vec4 viewPos = view * model * vec4(aPos, 1.0);
    float dist   = length(viewPos.xyz);

    // Point size: large when close, tiny when far.
    // Fireflies should be small — max ~18px, min ~3px
    float size = clamp(220.0 / dist, 3.0, 18.0) * (0.4 + 0.6 * aBrightness);
    gl_PointSize = size;

    gl_Position = projection * viewPos;
}
