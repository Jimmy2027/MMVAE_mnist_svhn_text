import typing
from pathlib import Path

import torch
import torchvision.transforms as transforms
from matplotlib import pyplot as plt
from torch import Tensor

from mmvae_hub.mimic.classifiers.train_img_clfs import LM
from mmvae_hub.modalities.ModalityIMG import ModalityIMG
from mmvae_hub.networks.images.ConvNetworksImgMimic import EncoderImg, DecoderImg
from modun.download_utils import download_zip_from_url


class LM_(LM):
    def __init__(self, str_labels: list, transforms):
        super().__init__(str_labels)
        self.transforms = transforms

    def forward(self, x):
        x_ = torch.cat([self.transforms(torch.cat([s for _ in range(3)])).unsqueeze(0) for s in x], dim=0).to(x.device)
        return self.model(x_)


class MimicImg(ModalityIMG):
    def __init__(self, data_size, flags, name, labels, rec_weight, plot_img_size):
        super().__init__(data_size, flags, name)
        self.labels = labels

        self.labels = labels
        self.gen_quality_eval = True
        self.file_suffix = '.png'

        self.encoder = EncoderImg(self.flags).to(flags.device)
        self.decoder = DecoderImg(self.flags).to(flags.device)

        self.rec_weight = rec_weight

        self.plot_img_size = plot_img_size

        self.clf_transforms = transforms.Compose([
            transforms.ToPILImage(),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.Resize(256),
            transforms.CenterCrop(256),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
        ])

        self.clf = self.get_clf()

    def get_clf(self):
        if self.flags.use_clf:
            clf_name_mapping = {'PA': 'pa', 'Lateral': 'lat'}
            # finding the directory of the classifier
            img_clf_path = Path(
                __file__).parent.parent / f'classifiers/state_dicts/{clf_name_mapping[self.name]}_clf_{self.flags.img_size}.pth'
            if not img_clf_path.exists():
                download_zip_from_url(
                    url='http://jimmy123.hopto.org:2095/nextcloud/index.php/s/GTc8pYiDKrq35ky/download',
                    dest_folder=img_clf_path.parent.parent, verbose=True)
            lightning_module = LM_(str_labels=self.labels, transforms=self.clf_transforms)
            lightning_module.model.load_state_dict(
                torch.load(img_clf_path, map_location=self.flags.device))
            return lightning_module.to(self.flags.device)

    def plot_data_single_img(self, d: Tensor):
        return plt.imshow(self.plot_data(d.squeeze(dim=0)).cpu().detach().squeeze(), cmap='gray')


class MimicPA(MimicImg):
    def __init__(self, flags, labels: typing.Iterable[str], rec_weight, plot_img_size):
        data_size = torch.Size((1, flags.img_size, flags.img_size))
        super().__init__(data_size=data_size, flags=flags, name='PA', labels=labels, rec_weight=rec_weight,
                         plot_img_size=plot_img_size)


class MimicLateral(MimicImg):
    def __init__(self, flags, labels: typing.Iterable[str], rec_weight, plot_img_size):
        data_size = torch.Size((1, flags.img_size, flags.img_size))
        super().__init__(data_size=data_size, flags=flags, name='Lateral', labels=labels, rec_weight=rec_weight,
                         plot_img_size=plot_img_size)


if __name__ == '__main__':
    img_clf_path = Path(
        __file__).parent.parent / f'classifiers/state_dicts/pa_clf_128.pth'
    if not img_clf_path.exists():
        download_zip_from_url(
            url='http://jimmy123.hopto.org:2095/nextcloud/index.php/s/GTc8pYiDKrq35ky/download',
            dest_folder=img_clf_path.parent.parent, verbose=True)
