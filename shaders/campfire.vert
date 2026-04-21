#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
layout(location = 2) in float aLife;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float time;

out vec3 Color;
out float Life;
out float PointSize;

void main() {
    Color = aColor;
    Life = aLife;

    vec4 viewPos = view * model * vec4(aPos, 1.0);
    float dist = length(viewPos.xyz);
    PointSize = max(2.0, 80.0 / dist) * aLife;

    gl_Position = projection * viewPos;
    gl_PointSize = PointSize;
}
