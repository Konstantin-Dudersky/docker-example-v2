"""Изменение тегов в образах."""

import logging
import subprocess

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class DockerComposeProfile:
    __profile: str

    def __init__(self, profile: str) -> None:
        self.__profile = profile

    def __pull_images(
        self,
        images: list[str],
        repo_from: str,
        arch: str = "linux/amd64",
    ) -> None:
        log.debug(
            "pulling images from repo: {0}, arch: {1}".format(
                repo_from,
                arch,
            )
        )
        cmd: str = "docker pull --platform {arch} {repo_from}/{image}"
        for image in images:
            subprocess.run(
                args=cmd.format(
                    arch=arch,
                    image=image,
                    repo_from=repo_from,
                ).split(),
            )

    def __push_images(self, images: list[str], repo_to: str) -> None:
        cmd: str = "docker push {repo_to}/{image}"
        for image in images:
            subprocess.run(
                cmd.format(
                    image=image,
                    repo_to=repo_to,
                ).split()
            )

    def __get_images_from_compose(self, profile: str) -> list[str]:
        cmd: str = "docker compose --profile {profile} config --images"
        images = (
            subprocess.run(
                args=cmd.format(profile=profile).split(),
                capture_output=True,
                text=True,
            )
            .stdout.strip()
            .split("\n")
        )
        return images

    def __remove_repo(self, images: list[str], repo: str) -> list[str]:
        images_wo_repo: list[str] = []
        for image in images:
            if repo not in image:
                raise ValueError("incorrect repo in image {0}".format(image))
            image_wo_repo = image.replace(repo + "/", "")
            images_wo_repo.append(image_wo_repo)
        return images_wo_repo

    def __add_tag(
        self,
        images: list[str],
        repo_from: str,
        repo_to: str,
    ) -> None:
        cmd: str = "docker tag {repo_from}/{image} {repo_to}/image"
        for image in images:
            subprocess.run(
                cmd.format(
                    image=image,
                    repo_from=repo_from,
                    repo_to=repo_to,
                ).split()
            )

    def copy_images_between_repos(
        self,
        repo_from: str,
        repo_to: str,
        arch: str = "linux/amd64",
    ) -> None:
        target_images = self.__get_images_from_compose(self.__profile)
        log.info("target images: \n{0}\n".format(target_images))
        images_wo_repo = self.__remove_repo(
            images=target_images,
            repo=repo_to,
        )
        log.info("images w/o repo: \n{0}\n".format(images_wo_repo))
        self.__pull_images(images_wo_repo, repo_from, arch)
        self.__add_tag(
            images=images_wo_repo,
            repo_from=repo_from,
            repo_to=repo_to,
        )
        self.__push_images(images_wo_repo, repo_to)


if __name__ == "__main__":
    log.addHandler(logging.StreamHandler())
    DockerComposeProfile(profile="server",).copy_images_between_repos(
        repo_from="localhost:5000",
        repo_to="target:5000",
        arch="linux/arm64",
    )
