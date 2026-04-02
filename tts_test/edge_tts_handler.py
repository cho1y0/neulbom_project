"""
Edge TTS 핸들러
Microsoft Edge의 다양한 한국어 음성 지원

✅ 개선 포인트(최소 변경):
- "보미(다정)" 프리셋(preset) 추가: 목소리/속도/피치/볼륨을 한 번에 적용
- pitch(Hz) 지원 추가 (edge-tts에서 rate/volume/pitch 조절 가능)
- "다정한 말하기"를 위해 문장 끝에 줄바꿈을 자동 삽입(자연스러운 쉬는 구간 유도)
  ※ edge-tts는 커스텀 SSML이 제한되는 환경이어서 <break> 같은 태그를 직접 넣는 방식은 권장되지 않습니다.
"""

import os
import asyncio
import re
import tempfile
import shutil


class EdgeTTSHandler:
    """Edge TTS 핸들러 (다양한 한국어 목소리)"""

    # 한국어 음성 목록
    VOICES = {
        # 여성 음성
        "sun-hi": "ko-KR-SunHiNeural",        # 여성 1 (밝고 친절)
        "ji-min": "ko-KR-JiMinNeural",        # 여성 2 (차분함)
        "seo-hyeon": "ko-KR-SeoHyeonNeural",  # 여성 3 (부드러움)
        "soon-bok": "ko-KR-SoonBokNeural",    # 여성 4 (할머니 느낌)
        "yu-jin": "ko-KR-YuJinNeural",        # 여성 5 (젊음)

        # 남성 음성
        "in-joon": "ko-KR-InJoonNeural",      # 남성 1 (차분함)
        "hyun-su": "ko-KR-HyunsuNeural",      # 남성 2 (명랑)
        "bong-jin": "ko-KR-BongJinNeural",    # 남성 3 (할아버지 느낌)
        "gook-min": "ko-KR-GookMinNeural",    # 남성 4 (젊음)
    }

    # 프리셋: "다정한 보미"를 빠르게 적용하기 위한 값
    # - rate: 느리게(-) / 빠르게(+)
    # - pitch: Hz 단위 (예: -10Hz는 살짝 낮게)
    PRESETS = {
        # 기본(기존과 최대한 유사)
        "default": {"voice": "sun-hi", "rate": "+0%", "volume": "+0%", "pitch": "+0Hz"},

        # 보미(다정) 추천: 부드러운 목소리 + 약간 느리게 + 피치 살짝 낮게
        "bomi": {"voice": "seo-hyeon", "rate": "-10%", "volume": "+0%", "pitch": "-10Hz"},

        # 보미(더 차분): 더 느리게, 더 안정감
        "bomi_calm": {"voice": "ji-min", "rate": "-15%", "volume": "+0%", "pitch": "-15Hz"},
    }

    def __init__(self, voice=None, rate=None, volume=None, pitch=None, preset="bomi"):
        """
        Args:
            voice: 음성 선택 (VOICES 키 또는 전체 음성명)
            rate: 속도 (+0% = 보통, +10% = 빠름, -10% = 느림)
            volume: 볼륨 (+0% = 보통, +10% = 크게, -10% = 작게)
            pitch: 피치 ('+0Hz', '-10Hz' 등)
            preset: 프리셋 이름 (default / bomi / bomi_calm)
                    ※ voice/rate/volume/pitch를 직접 넣으면 preset보다 우선 적용됩니다.
        """
        try:
            import edge_tts
            self.edge_tts = edge_tts
        except ImportError:
            print("❌ edge-tts가 설치되지 않았습니다.")
            print("   설치: pip install edge-tts")
            raise

        # 1) 프리셋 적용
        preset_conf = self.PRESETS.get(preset, self.PRESETS["default"]).copy()

        # 2) 사용자가 직접 지정한 값은 프리셋보다 우선
        final_voice = voice if voice is not None else preset_conf["voice"]
        self.rate = rate if rate is not None else preset_conf["rate"]
        self.volume = volume if volume is not None else preset_conf["volume"]
        self.pitch = pitch if pitch is not None else preset_conf["pitch"]

        # 음성 선택
        if final_voice in self.VOICES:
            self.voice = self.VOICES[final_voice]
            self.voice_name = final_voice
        else:
            # 전체 음성명을 직접 넣는 경우
            self.voice = final_voice
            self.voice_name = final_voice

        self.preset = preset

        print(
            f"✅ Edge TTS 초기화 완료 (preset: {self.preset}, 목소리: {self.voice_name}, "
            f"rate: {self.rate}, pitch: {self.pitch}, volume: {self.volume})"
        )

    # -------------------------
    # 공개 API
    # -------------------------
    def speak(self, text, save_to_file=None):
        """
        텍스트를 음성으로 변환 및 재생

        Args:
            text: 읽을 텍스트
            save_to_file: MP3 파일로 저장할 경로 (선택)
        """
        if not text or not str(text).strip():
            print("⚠️  텍스트가 비어있습니다.")
            return

        try:
            asyncio.run(self._speak_async(str(text), save_to_file))
        except RuntimeError:
            # 이미 이벤트 루프가 돌고 있는 환경(Jupyter 등) 대비
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.run_until_complete(self._speak_async(str(text), save_to_file))
        except Exception as e:
            print(f"❌ TTS 오류: {e}")

    def list_voices(self):
        """사용 가능한 목소리 목록 출력"""
        print("\n" + "=" * 60)
        print("🎤 사용 가능한 한국어 목소리")
        print("=" * 60)

        print("\n[여성 음성]")
        for name, voice in list(self.VOICES.items())[:5]:
            print(f"  {name:15s} - {voice}")

        print("\n[남성 음성]")
        for name, voice in list(self.VOICES.items())[5:]:
            print(f"  {name:15s} - {voice}")

        print("\n프리셋 사용법: EdgeTTSHandler(preset='bomi')")
        print("직접 설정: EdgeTTSHandler(voice='seo-hyeon', rate='-10%', pitch='-10Hz')")
        print("=" * 60)

    def set_voice(self, voice):
        """목소리 변경"""
        if voice in self.VOICES:
            self.voice = self.VOICES[voice]
            self.voice_name = voice
            print(f"✅ 목소리 변경: {self.voice_name}")
        else:
            # 전체 음성명을 직접 넣는 경우도 허용
            self.voice = voice
            self.voice_name = voice
            print(f"✅ 목소리 변경(직접 지정): {self.voice_name}")

    def set_rate(self, rate):
        """속도 변경 (예: '+10%', '-10%', '+0%')"""
        self.rate = rate
        print(f"✅ 속도 변경: {rate}")

    def set_volume(self, volume):
        """볼륨 변경 (예: '+10%', '-10%', '+0%')"""
        self.volume = volume
        print(f"✅ 볼륨 변경: {volume}")

    def set_pitch(self, pitch):
        """피치 변경 (예: '+0Hz', '-10Hz', '+20Hz')"""
        self.pitch = pitch
        print(f"✅ 피치 변경: {pitch}")

    def set_preset(self, preset: str):
        """
        프리셋 변경 (voice/rate/volume/pitch를 한 번에 적용)
        """
        if preset not in self.PRESETS:
            print(f"⚠️  알 수 없는 preset: {preset} (가능: {list(self.PRESETS.keys())})")
            return

        conf = self.PRESETS[preset]
        self.preset = preset
        self.set_voice(conf["voice"])
        self.set_rate(conf["rate"])
        self.set_volume(conf["volume"])
        self.set_pitch(conf["pitch"])

    # -------------------------
    # 내부 로직
    # -------------------------
    async def _speak_async(self, text, save_to_file=None):
        """비동기 음성 생성"""
        is_temp_file = not save_to_file
        temp_file_obj = None

        if is_temp_file:
            # 고유한 임시 파일 생성
            temp_file_obj = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            filename = temp_file_obj.name
            temp_file_obj.close()  # 파일을 닫아 edge-tts가 쓸 수 있도록 함
        else:
            filename = self._resolve_filename(save_to_file)

        # 경로 폴더 생성
        out_dir = os.path.dirname(filename)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # "다정하게" 들리도록 텍스트를 약간 가공(줄바꿈/쉼 유도)
        speak_text = self._preprocess_text(text)

        communicate = self.edge_tts.Communicate(
            text=speak_text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume,
            pitch=self.pitch,
        )

        await communicate.save(filename)
        print(f"💾 음성 생성: {filename}")

        self._play_audio(filename)

        if is_temp_file and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception:
                pass

    def _resolve_filename(self, save_to_file):
        """저장 파일명 결정(.wav 요청 시 .mp3로 변환)"""
        if save_to_file:
            if save_to_file.endswith(".wav"):
                return save_to_file.replace(".wav", ".mp3")
            return save_to_file
        return "./temp_edge_tts.mp3"  # 이 경로는 is_temp_file=False일 때만 참조됨

    def _preprocess_text(self, text: str) -> str:
        """
        자연스러운 쉬는 구간을 만들기 위한 최소 가공입니다.
        - 문장 끝(., ?, !) 뒤에 줄바꿈을 넣어 쉬는 구간을 유도
        - 너무 긴 공백/줄바꿈 정리
        """
        t = (text or "").strip()

        # 문장 끝에 줄바꿈 삽입
        t = re.sub(r"([.?!。！？])\s*", r"\1\n", t)

        # 쉼표 뒤 공백 정리
        t = re.sub(r",\s*", ", ", t)

        # 줄바꿈 3개 이상은 2개로 제한
        t = re.sub(r"\n{3,}", "\n\n", t)

        return t

    def _play_audio(self, filename):
        """오디오 재생 (Windows/macOS/Linux 대응 + 플레이어 자동 탐색)"""
        import platform
        system = platform.system()

        try:
            if system == "Windows":
                try:
                    from playsound3 import playsound
                    playsound(filename)
                    return
                except ImportError:
                    print("⚠️  playsound3 미설치, 파일만 저장됨")
                    return

            if system == "Darwin":  # macOS
                os.system(f"afplay \"{filename}\"")
                return

            # Linux: 사용 가능한 플레이어를 찾아 실행
            for cmd in ("mpv", "mpg123", "ffplay"):
                if shutil.which(cmd):
                    if cmd == "ffplay":
                        os.system(f"{cmd} -nodisp -autoexit \"{filename}\" >/dev/null 2>&1")
                    else:
                        os.system(f"{cmd} \"{filename}\" >/dev/null 2>&1")
                    return

            print("⚠️  재생 도구(mpv/mpg123/ffplay)를 찾지 못했습니다. 파일만 저장되었습니다.")

        except Exception as e:
            print(f"⚠️  재생 실패: {e}")


# ========== 테스트 ==========
if __name__ == "__main__":
    print("=" * 60)
    print("🎤 Edge TTS 테스트")
    print("=" * 60)

    # 프리셋(보미)로 테스트
    tts = EdgeTTSHandler(preset="bomi")
    tts.list_voices()

    test_voices = ["sun-hi", "seo-hyeon", "soon-bok", "in-joon", "bong-jin"]
    test_text = "할머니, 저 보미예요. 오늘도 편안하게 지내셨지요?"

    print("\n" + "=" * 60)
    print("🔊 목소리별 테스트")
    print("=" * 60)

    for v in test_voices:
        print(f"\n▶ {v} 목소리:")
        tts = EdgeTTSHandler(voice=v, rate="-10%", pitch="-10Hz", preset="bomi")
        tts.speak(test_text)
        input("   [Enter를 눌러 다음 목소리...]")

    print("\n✅ 테스트 완료!")