from enum import Enum


class IMG_TYPE(Enum):
    ICON = 0
    FORMULA = 1

class ImgInfo:
    # root_path = "image: url(:/Formula/img/complex_permittivity.png);"
    def __init__(self,imag_type:IMG_TYPE,img_name:str):
        if imag_type is IMG_TYPE.ICON:
            self.type_str = "Icon"
        elif imag_type is IMG_TYPE.FORMULA:
            self.type_str = "Formula"
        else:
            self.type_str = "Unknown"
        self.img_name = img_name
    def get_img_path(self):
        return f"image: url(:/{self.type_str}/img/{self.img_name}.png);"
    def get_src_path(self):
        return f"qrc:/{self.type_str}/img/{self.img_name}.png"

img_path_dict={}
img_path_dict["central_distance"] = ImgInfo(IMG_TYPE.FORMULA,"central_distance")
img_path_dict["d_12"] = ImgInfo(IMG_TYPE.FORMULA,"central_distance")
img_path_dict["number_density"] = ImgInfo(IMG_TYPE.FORMULA,"number_density")
img_path_dict["n_p"] = ImgInfo(IMG_TYPE.FORMULA,"number_density")
img_path_dict["charging_energy"] = ImgInfo(IMG_TYPE.FORMULA,"charging_energy")
img_path_dict["E_12"] = ImgInfo(IMG_TYPE.FORMULA,"charging_energy")
img_path_dict["charging_energy_1"] = ImgInfo(IMG_TYPE.FORMULA,"charging_energy_1")
img_path_dict["E_c1"] = ImgInfo(IMG_TYPE.FORMULA,"charging_energy_1")
img_path_dict["charging_energy_2"] = ImgInfo(IMG_TYPE.FORMULA,"charging_energy_2")
img_path_dict["E_c2"] = ImgInfo(IMG_TYPE.FORMULA,"charging_energy_2")
img_path_dict["epsilon_prime"] = ImgInfo(IMG_TYPE.FORMULA,"complex_permittivity")
img_path_dict["epsilon_prime_prime"] = ImgInfo(IMG_TYPE.FORMULA,"complex_permittivity")
img_path_dict["complex_permittivity"] = ImgInfo(IMG_TYPE.FORMULA,"complex_permittivity")
img_path_dict["kappa"] = ImgInfo(IMG_TYPE.FORMULA,"decay_rate")
img_path_dict["decay_rate"] = ImgInfo(IMG_TYPE.FORMULA,"decay_rate")
img_path_dict["diameter_1"] = ImgInfo(IMG_TYPE.FORMULA,"diameter_1")
img_path_dict["d_1"] = ImgInfo(IMG_TYPE.FORMULA,"diameter_1")
img_path_dict["diameter_2"] = ImgInfo(IMG_TYPE.FORMULA,"diameter_2")
img_path_dict["d_2"] = ImgInfo(IMG_TYPE.FORMULA,"diameter_2")
img_path_dict["tau_0"] = ImgInfo(IMG_TYPE.FORMULA,"dielectric_relaxation_time_0")
img_path_dict["dielectric_relaxation_time_0"] = ImgInfo(IMG_TYPE.FORMULA,"dielectric_relaxation_time_0")
img_path_dict["tau_m"] = ImgInfo(IMG_TYPE.FORMULA,"dielectric_relaxation_time_m")
img_path_dict["dielectric_relaxation_time_m"] = ImgInfo(IMG_TYPE.FORMULA,"dielectric_relaxation_time_m")
img_path_dict["delta_epsilon"] = ImgInfo(IMG_TYPE.FORMULA,"dielectric_strength")
img_path_dict["dielectric_strength"] = ImgInfo(IMG_TYPE.FORMULA,"dielectric_strength")
img_path_dict["potential_height"] = ImgInfo(IMG_TYPE.FORMULA,"potential_height")
img_path_dict["U"] = ImgInfo(IMG_TYPE.FORMULA,"potential_height")
img_path_dict["spacing"] = ImgInfo(IMG_TYPE.FORMULA,"spacing")
img_path_dict["s"] = ImgInfo(IMG_TYPE.FORMULA,"spacing")
img_path_dict["volume"] = ImgInfo(IMG_TYPE.FORMULA,"volume")
img_path_dict["V"] = ImgInfo(IMG_TYPE.FORMULA,"volume")





if __name__=="__main__":
    print(img_path_dict["epsilon_prime"].get_path())

