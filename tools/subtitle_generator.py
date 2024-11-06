from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type, List, Dict
import json
import logging
from datetime import datetime, timedelta

class SubtitleInput(BaseModel):
    text: str
    timestamps: Optional[List[Dict]] = None

class SubtitleGenerator(BaseTool):
    name: str = Field(default="subtitle_generator")
    description: str = Field(default="生成SRT格式字幕")
    args_schema: Type[BaseModel] = Field(default=SubtitleInput)

    def _run(self, text: str, timestamps: Optional[List[Dict]] = None) -> str:
        """生成SRT格式字幕
        
        Args:
            text: 识别出的文本
            timestamps: 时间戳列表 [{"start_time": 1000, "end_time": 2000, "text": "文本"}]
        
        Returns:
            SRT格式的字幕文本
        """
        try:
            if not timestamps:
                # 如果没有时间戳，按照固定长度分割文本
                return self._generate_simple_srt(text)
            
            return self._generate_timed_srt(timestamps)
            
        except Exception as e:
            logging.error(f"生成字幕错误: {str(e)}")
            raise

    def _generate_simple_srt(self, text: str) -> str:
        """生成简单的SRT字幕（固定时间间隔）"""
        try:
            # 按标点符号分割文本
            sentences = [s.strip() for s in text.replace('。', '。\n').split('\n') if s.strip()]
            
            srt_lines = []
            for i, sentence in enumerate(sentences, 1):
                # 每句话假设3秒
                start_time = timedelta(seconds=(i-1)*3)
                end_time = timedelta(seconds=i*3)
                
                srt_lines.extend([
                    str(i),
                    f"{self._format_timedelta(start_time)} --> {self._format_timedelta(end_time)}",
                    sentence,
                    ""
                ])
            
            return "\n".join(srt_lines)
            
        except Exception as e:
            logging.error(f"生成简单字幕错误: {str(e)}")
            raise

    def _generate_timed_srt(self, timestamps: List[Dict]) -> str:
        """生成带时间戳的SRT字幕"""
        try:
            srt_lines = []
            for i, item in enumerate(timestamps, 1):
                start_time = self._ms_to_timedelta(item['start_time'])
                end_time = self._ms_to_timedelta(item['end_time'])
                
                srt_lines.extend([
                    str(i),
                    f"{self._format_timedelta(start_time)} --> {self._format_timedelta(end_time)}",
                    item['text'],
                    ""
                ])
            
            return "\n".join(srt_lines)
            
        except Exception as e:
            logging.error(f"生成时间戳字幕错误: {str(e)}")
            raise

    def _format_timedelta(self, td: timedelta) -> str:
        """格式化时间为SRT格式 (HH:MM:SS,mmm)"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = int(td.microseconds / 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def _ms_to_timedelta(self, ms: int) -> timedelta:
        """将毫秒转换为timedelta"""
        return timedelta(milliseconds=ms)

    async def _arun(self, text: str, timestamps: Optional[List[Dict]] = None) -> str:
        """异步实现（如果需要）"""
        raise NotImplementedError("异步生成暂未实现") 