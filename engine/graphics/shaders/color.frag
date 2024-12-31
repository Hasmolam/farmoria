#version 330

uniform sampler2D texture0;

in vec2 v_texcoord;
in vec4 v_color;
out vec4 f_color;

void main() {
    vec4 tex_color = texture(texture0, v_texcoord);
    f_color = tex_color * v_color;
} 