#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
layout(location = 2) in float aLife;
layout(location = 3) in float aSizeMult;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float time;

out vec3 Color;
out float Life;
out float PointSize;

void main() {
    Color = aColor;
    Life  = aLife;

    vec4 viewPos = view * model * vec4(aPos, 1.0);
    float dist   = length(viewPos.xyz);

    // Tutorial concept: particle starts large (young/hot) and shrinks as life drops.
    // aSizeMult controls per-type base size (core > flame > ember > smoke).
    // aLife scales it down so each particle visually "burns out" and shrinks.
    float baseSize = 110.0 * aSizeMult / dist;
    PointSize = clamp(baseSize * aLife, 1.2, 56.0);

    gl_Position  = projection * viewPos;
    gl_PointSize = PointSize;
}
