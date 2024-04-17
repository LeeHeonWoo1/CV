### Set Env for training tesseract
pytesseract의 경우 windows에서 제약이 많은 편이다. 따라서 wsl2를 설치하고, linux환경에서 custom training하여 ocr하는 식으로 진행한다.
- Tesseract는 아래 세 가지 방식으로 학습시킬 수 있다.
    + Fine Tuning : pre training model에 custom training
    + Transfer learning : pre training model의 Affine 계층 제외, 전이학습
    + Custom Training : 가지고 있는 데이터셋이 많다는 가정 하에, 아예 모델을 처음부터 훈련시킬 수 있다.

1. wsl2 설치
    - https://www.lainyzine.com/ko/article/a-complete-guide-to-how-to-install-docker-desktop-on-windows-10/#google_vignette
    - 위 링크를 따라 wsl2를 설치하면 기본 ubuntu 버전까지 깔아진다.
  
2. Install Package for Tesseract(4.1.1 ver)
    - 필요한 라이브러리 설치

```terminal
# 소스코드빌드 관련 패키지 설치
$ sudo apt install automake
$ sudo apt install libtool
$ sudo apt install autoconf

# 개발 관련 라이브러리 설치
$ sudo apt install curl
$ sudo apt install openjdk-11-jdk

# 기타 필요한 패키지
$ sudo apt install pkg-config
$ sudo apt install build-essential
$ sudo apt install clang
$ sudo apt install libleptonica-dev
$ sudo apt install tesseract-ocr
```

3. Install Tesseract

```terminal
# 작업할 경로로 이동 후 wsl 실행, tesseract 메인 소스코드 다운로드
$ wget wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/4.1.1.tar.gz
$ tar xvf 4.1.1.tar.gz
$ git clone https://github.com/tesseract-ocr/tessdata_best.git
$ git clone https://github.com/tesseract-ocr/langdata.git
```

각 폴더의 용도는 아래와 같다.
- tesseract : 학습을 포함한 대부분의 명령 구문을 사용할 메인 폴더
- langdata : 학습에 필요한 언어별 설정 폴더
- tessdata_best : tesseract에서 제공하는 모델 중 가장 좋은 성능을 보이는 모델 폴더
    + legacy모델이나 기타 다른 모델이 필요한 경우 해당 폴더를 사용하자.

위 과정을 모두 실행하고 나면 아래와 같이 구조를 정리하자
```
(~root)
   |--- tesseract (renamed from tesseract-4.1.1)
   |--- tessdata_best
   |___ langdata
```

4. 소스코드 빌드 환경 구축 및 결과 확인
내려받은 소스코드를 빌드하기 위한 환경을 구축한다.

```terminal
$ cd tesseract
$ ./autogen.sh

# 소스코드 빌드 환경 구축 결과 확인
$ ./configure
```

아래와 같은 화면이 보인다면 환경 구축은 완료된 것이다.

```
...
Configuration is done.
You can now build and install tesseract by running:

$ make
$ sudo make install
$ sudo ldconfig

Documentation will not be built because asciidoc or xsltproc is missing.

You can not build training tools because of missing dependency.
Check configure output for details.
```

5. if non-gpu or use docker..
    - 도커를 사용하는 환경이거나, gpu 컴퓨팅이 지원되지 않는 환경에서는 아래 설정을 진행해줘야 정상적으로 동작한다고 한다.
    > `$ ./config --disable-graphics`
    - cuda 설정이 되어 있기에 건너뛴다.
  
6. training tools를 위한 빌드
```
# build training tools
$ make
$ cd ..
```

7. 훈련 데이터 복사
    - 사전에 훈련된 데이터를 다시 사용하기 위해 tesseract로 복사한다.

```terminal
$ cp./tessdata_best/kor.traineddata ./tesseract/tessdata/
$ cp -r ./langdata/kor ./tesseract/langdata/kor/
$ gedit ./tesseract/langdata/for/for.training_text
```

8. workspace 디렉토리 생성

```terminal
$ mkdir -p workspace/train
$ mkdir -p workspace/base_lstm
$ mkdir -p workspace/output
```

9. 학습 준비
```terminal
$ cd tesseract
$ src/training/tesstrain.sh \
--fonts_dir ./fonts \
--lang kor \
--linedata_only \
--noextract_font_properties \
--langdata_dir ./langdata \
--tessdata_dir ./tessdata \
--exposures "0" \
--fontlist "Malgun Gothic" \
--output_dir ../workspace/train
```

10. 학습
```terminal
$ combine_tessdata -e ./tessdata/kor.traineddata ../workspace/base_lstm/kor.lstm
$ lstmtraining \
--continue_from ../workspace/base_lstm/kor.lstm \
--old_traineddata ./tessdata/kor.traineddata \
--traineddata ../workspace/train/kor/kor.traineddata \
--model_output ../workspace/output/base \
--train_listfile ../workspace/train/kor.training_files.txt \
--max_iterations 3600
```

11. 모델 배포
```terminal
lstmtraining \
--stop_training \
--continue_from ../workspace/output/base_checkpoint \
--old_traineddata ./tessdata/kor.traineddata \
--traineddata ../workspace/train/kor/kor.traineddata \
--model_output ../workspace/output/kor.traineddata
```

12. 모델 테스트
```terminal
tesseract ../workspace/images/image-11.png stdout -l kor --oem 1 --psm 3 --tessdata-dir ../workspace/output
```