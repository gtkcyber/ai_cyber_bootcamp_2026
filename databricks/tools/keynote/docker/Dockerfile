# LibreOffice and ffmpeg for the Keynote build, pinned to what the course
# decks need: Impress with the Keynote importer, the decks' two faces
# (Orbitron for titles, Titillium Web for body text, both OFL) and fontconfig
# aliases mapping the PostScript family names the importer emits onto
# installed fonts. Built by `keynote build` when missing, or by hand:
#
#     docker build -t bootcamp-keynote databricks/tools/keynote/docker
FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        libreoffice-impress ffmpeg fonts-liberation fonts-dejavu fonts-noto-core \
        fonts-open-sans fonts-crosextra-carlito fontconfig ca-certificates \
    && rm -rf /var/lib/apt/lists/*
ADD https://github.com/google/fonts/raw/main/ofl/orbitron/Orbitron%5Bwght%5D.ttf /usr/local/share/fonts/Orbitron.ttf
ADD https://github.com/google/fonts/raw/main/ofl/titilliumweb/TitilliumWeb-Regular.ttf /usr/local/share/fonts/TitilliumWeb-Regular.ttf
ADD https://github.com/google/fonts/raw/main/ofl/titilliumweb/TitilliumWeb-Bold.ttf /usr/local/share/fonts/TitilliumWeb-Bold.ttf
ADD https://github.com/google/fonts/raw/main/ofl/titilliumweb/TitilliumWeb-Light.ttf /usr/local/share/fonts/TitilliumWeb-Light.ttf
ADD https://github.com/google/fonts/raw/main/ofl/titilliumweb/TitilliumWeb-SemiBold.ttf /usr/local/share/fonts/TitilliumWeb-SemiBold.ttf
COPY local.conf /etc/fonts/local.conf
RUN chmod 644 /usr/local/share/fonts/*.ttf && fc-cache -f
WORKDIR /work
