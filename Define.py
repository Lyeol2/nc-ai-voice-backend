from pydantic import BaseModel
from abc import ABC, abstractmethod

# 프롬포트로 직렬화가능한 모델
class SerializablePromptModel(BaseModel):
    @abstractmethod
    def Serialize():
        pass


# ===== NPC 세팅 모델 =====
class NPCCueInfo(SerializablePromptModel):
    unlockTrustLevel : int
    cueMsg : str

    def Serialize(self):
        return self.queMsg


class NPCInfo(SerializablePromptModel):
    npcID : int
    npcName : str
    backgroundPrompt : str 
    personalityPrompt : str
    cueInfo : list[NPCCueInfo]

    def Serialize(self) -> str:
        return f"""# 기본 정보"
        아이디 : {self.npcID}
        이름 : {self.npcName}
        배경상황 : {self.backgroundPrompt}
        성격 : {self.personalityPrompt}
        """

class Session(SerializablePromptModel):
    uuid : str
    sessionType : int
    npcInfo : NPCInfo
    currentTrustLevel : int

    def Serialize(self) -> str:
        return self.npcInfo.Serialize()








# ===== 요청/응답 모델 =====
class ChatRequest(BaseModel):
    sessionUUID : str
    message: str

class ChatResponse(BaseModel):
    reply: str

# ===== 사운드 요청/응답 모델 =====

class SoundRequest(BaseModel):
    voice : str
    language : str 
    text : str   

class SoundResponse(BaseModel):
    soundWAV : str


# ===== 기본 응답 모델 =====
class Response(BaseModel):
    code : int
    msg : str