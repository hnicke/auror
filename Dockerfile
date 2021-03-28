FROM archlinux:base-devel

RUN yes | pacman -Sy pacman-contrib git

RUN useradd -m makepkg
# Allow notroot to run stuff as root (to install dependencies):
RUN echo "makepkg ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/makepkg
USER makepkg
WORKDIR /home/makepkg

RUN git clone https://aur.archlinux.org/yay-bin.git && \
    cd yay-bin && \
    makepkg --noconfirm --syncdeps --rmdeps --install --clean


