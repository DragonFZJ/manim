from helpers import *

from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import *

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.continual_animation import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.fractals import *
from topics.number_line import *
from topics.combinatorics import *
from topics.numerals import *
from topics.three_dimensions import *
from topics.objects import *
from topics.probability import *
from topics.complex_numbers import *
from scene import Scene
from scene.reconfigurable_scene import ReconfigurableScene
from scene.zoomed_scene import *
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *

E_COLOR = BLUE
M_COLOR = RED

class OscillatingVector(ContinualAnimation):
    CONFIG = {
        "tail" : ORIGIN,
        "frequency" : 1,
        "A_x" : 1,
        "A_y" : 0,
        "phi_x" : 0,
        "phi_y" : 0,
        "vector_to_be_added_to" : None,
    }
    def setup(self):
        self.vector = self.mobject

    def update_mobject(self, dt):
        f = self.frequency
        t = self.internal_time
        angle = 2*np.pi*f*t
        vect = np.array([
            self.A_x*np.exp(complex(0, angle + self.phi_x)),
            self.A_y*np.exp(complex(0, angle + self.phi_y)),
            0,
        ]).real
        self.update_tail()
        self.vector.put_start_and_end_on(self.tail, self.tail+vect)

    def update_tail(self):
        if self.vector_to_be_added_to is not None:
            self.tail = self.vector_to_be_added_to.get_end()

class OscillatingVectorComponents(ContinualAnimationGroup):
    CONFIG = {
        "tip_to_tail" : False,
    }
    def __init__(self, oscillating_vector, **kwargs):
        digest_config(self, kwargs)
        vx = Vector(UP, color = GREEN).fade()
        vy = Vector(UP, color = RED).fade()
        kwargs = {
            "frequency" : oscillating_vector.frequency,
            "tail" : oscillating_vector.tail,
        }
        ovx = OscillatingVector(
            vx,
            A_x = oscillating_vector.A_x,
            phi_x = oscillating_vector.phi_x,
            A_y = 0,
            phi_y = 0,
            **kwargs
        )
        ovy = OscillatingVector(
            vy,
            A_x = 0,
            phi_x = 0,
            A_y = oscillating_vector.A_y,
            phi_y = oscillating_vector.phi_y,
            **kwargs
        )
        components = [ovx, ovy]
        self.vectors = VGroup(ovx.vector, ovy.vector)
        if self.tip_to_tail:
            ovy.vector_to_be_added_to = ovx.vector
        else:
            self.lines = VGroup()
            for ov1, ov2 in (ovx, ovy), (ovy, ovx):
                ov_line = ov1.copy()
                ov_line.mobject = ov_line.vector = DashedLine(
                    UP, DOWN, color = ov1.vector.get_color()
                )
                ov_line.vector_to_be_added_to = ov2.vector
                components.append(ov_line)
                self.lines.add(ov_line.line)

        ContinualAnimationGroup.__init__(self, *components, **kwargs)

class EMWave(ContinualAnimationGroup):
    CONFIG = {
        "wave_number" : 3,
        "frequency" : 0.25,
        "n_vectors" : 40,
        "propogation_direction" : RIGHT,
        "start_point" : SPACE_WIDTH*LEFT,
        "length" : 2*SPACE_WIDTH,
        "amplitude" : 1,
        "rotation" : 0,
        "A_x" : 1,
        "A_y" : 0,
        "phi_x" : 0,
        "phi_y" : 0,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.matrix_transform = z_to_vector(self.propogation_direction)

        vector_oscillations = []
        self.E_vects = VGroup()
        self.M_vects = VGroup()

        A_multiplier = float(self.amplitude) / (self.A_x**2 + self.A_y**2)
        self.A_x *= A_multiplier
        self.A_y *= A_multiplier

        for alpha in np.linspace(0, 1, self.n_vectors):
            tail = interpolate(ORIGIN, self.length*OUT, alpha)
            phase = alpha*self.length*self.wave_number
            E_ov = OscillatingVector(
                Vector(UP, color = E_COLOR),
                tail = np.array(tail),
                A_x = self.A_x,
                A_y = self.A_y,
                phi_x = self.phi_x + phase,
                phi_y = self.phi_y + phase,
                frequency = self.frequency
            )
            M_ov = OscillatingVector(
                Vector(UP, color = M_COLOR),
                tail = np.array(tail),
                A_x = -self.A_y,
                A_y = self.A_x,
                phi_x = self.phi_y + phase,
                phi_y = self.phi_x + phase,
                frequency = self.frequency
            )
            vector_oscillations += [E_ov, M_ov]
            E_ov.vector.normal_vector = UP
            M_ov.vector.normal_vector = RIGHT
            self.E_vects.add(E_ov.vector)
            self.M_vects.add(M_ov.vector)
        ContinualAnimationGroup.__init__(self, *vector_oscillations)
        # make_3d(self.mobject)

    def update_mobject(self, dt):
        ContinualAnimationGroup.update_mobject(self, dt)
        # for vect in self.E_vects:
        #     vect.rotate_in_place(np.pi/2, RIGHT)
        # for vect in self.M_vects:
        #     vect.rotate_in_place(np.pi/2, UP)
        self.mobject.rotate(self.rotation, OUT)
        self.mobject.apply_matrix(self.matrix_transform)
        self.mobject.shift(self.start_point)

class WavePacket(Animation):
    CONFIG = {
        "EMWave_config" : {
            "wave_number" : 0,
            "start_point" : SPACE_WIDTH*LEFT,
        },
        "run_time" : 4,
        "rate_func" : None,
        "packet_width" : 6,
        "include_E_vects" : True,
        "include_M_vects" : True,
        "filter_distance" : SPACE_WIDTH,
        "get_filtered" : False,
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        em_wave = EMWave(**self.EMWave_config)
        em_wave.update(0)
        self.em_wave = em_wave

        self.vects = VGroup()
        if self.include_E_vects:
            self.vects.add(*em_wave.E_vects)
        if self.include_M_vects:
            self.vects.add(*em_wave.M_vects)
        for vect in self.vects:
            vect.save_state()

        u = em_wave.propogation_direction
        self.wave_packet_start, self.wave_packet_end = [
            em_wave.start_point - u*self.packet_width/2,
            em_wave.start_point + u*(em_wave.length + self.packet_width/2)
        ]
        Animation.__init__(self, self.vects, **kwargs)

    def update_mobject(self, alpha):
        packet_center = interpolate(
            self.wave_packet_start,
            self.wave_packet_end,
            alpha
        )
        em_wave = self.em_wave
        for vect in self.vects:
            tail = vect.get_start()
            distance_from_packet = np.dot(
                tail - packet_center,
                em_wave.propogation_direction
            )
            A = em_wave.amplitude*self.func(distance_from_packet)
            if np.abs(A) < 0.1:
                A = 0
            distance_from_start = np.linalg.norm(tail - em_wave.start_point)
            if self.get_filtered and distance_from_start > self.filter_distance:
                A = 0
            vect.restore()
            vect.scale(A/vect.get_length(), about_point = tail)

    def func(self, x):
        return np.sin(x)*np.exp(-0.5*x*x)

class FilterLabel(TexMobject):
    def __init__(self, tex, degrees, **kwargs):
        TexMobject.__init__(self, tex + " \\uparrow", **kwargs)
        self[-1].rotate(-degrees * np.pi / 180)

class PolarizingFilter(Circle):
    CONFIG = {
        "stroke_color" : DARK_GREY,
        "fill_color" : LIGHT_GREY,
        "fill_opacity" : 0.5,
        "label_tex" : None,
        "filter_angle" : 0,
    }
    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)

        if self.label_tex:
            self.label = TexMobject(self.label_tex)
            self.label.next_to(self.get_top(), DOWN, SMALL_BUFF)
            self.add(self.label)

        arrow = Arrow(ORIGIN, MED_LARGE_BUFF*UP, buff = 0)
        arrow.shift(self.get_top())
        arrow.rotate(-self.filter_angle)
        self.add(arrow)
        self.arrow = arrow

        arrow_label = TexMobject(
            "%.1f^\\circ"%(self.filter_angle*180/np.pi)
        )
        arrow_label.next_to(arrow.get_tip(), UP)
        self.add(arrow_label)
        self.arrow_label = arrow_label

class EMScene(Scene):
    def construct(self):
        pass


class TestCircularPolarization(ThreeDScene):
    def construct(self):
        self.add(ThreeDAxes())

        self.set_camera_position(0.8*np.pi/2, -0.6*np.pi)
        self.begin_ambient_camera_rotation(rate = 0.01)

        # pol_filter = PolarizingFilter(
        #     label_tex = "C",
        #     filter_angle = np.pi/4,
        # )
        # pol_filter.rotate(np.pi/2, RIGHT)
        # pol_filter.rotate(-np.pi/2, OUT)
        # pol_filter.shift(DOWN+OUT)
        # pol_filter.arrow_label.rotate_in_place(np.pi/4, OUT)
        # shade_in_3d(pol_filter)
        # self.add(pol_filter)

        wave = EMWave(wave_number = 1, A_y = 1, phi_y = np.pi/2)
        shade_in_3d(wave.mobject)
        self.add(wave)
        self.dither(20)
        # self.dither()
        # self.move_camera(theta = -1.2*np.pi/2)
        # self.play(WavePacket(
        #     run_time = 3,
        #     get_filtered = True,
        #     EMWave_config = {
        #         "start_point" : SPACE_WIDTH*LEFT + DOWN+OUT
        #     }            
        # ))
        # self.dither()





































