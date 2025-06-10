import os
from typing import Dict, Any
from openai import AsyncOpenAI
from app.domain.models import DocumentationRequest
from app.core.config import settings

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_documentation(self, parsed_code: Dict[str, Any], request: DocumentationRequest) -> Dict[str, Any]:
        """
        Genera documentación usando IA basada en el código parseado.
        """
        documentation = {}

        if request.generate_readme:
            documentation["readme"] = await self._generate_readme(parsed_code)

        if request.generate_comments:
            documentation["comments"] = await self._generate_comments(parsed_code)

        if request.generate_architecture:
            documentation["architecture"] = await self._generate_architecture(parsed_code)

        if request.generate_checklist:
            documentation["checklist"] = await self._generate_checklist(parsed_code)

        return documentation

    async def _generate_readme(self, parsed_code: Dict[str, Any]) -> str:
        prompt = f"""
        Genera un README.md completo para el siguiente proyecto:
        {parsed_code}
        
        El README debe incluir:
        - Descripción del proyecto
        - Instrucciones de instalación
        - Uso
        - Estructura del proyecto
        - Tecnologías utilizadas
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

    async def _generate_comments(self, parsed_code: Dict[str, Any]) -> list:
        prompt = f"""
        Analiza el siguiente código y genera comentarios de documentación para las funciones que no los tienen:
        {parsed_code}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

    async def _generate_architecture(self, parsed_code: Dict[str, Any]) -> str:
        prompt = f"""
        Genera un diagrama de arquitectura en formato Mermaid.js para el siguiente proyecto:
        {parsed_code}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

    async def _generate_checklist(self, parsed_code: Dict[str, Any]) -> list:
        prompt = f"""
        Genera una lista de verificación de buenas prácticas para el siguiente proyecto:
        {parsed_code}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content 