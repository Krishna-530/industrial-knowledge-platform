from typing import Dict, Optional, List, Tuple
from app.tools.models.tool_manifest import ToolManifest
from app.tools.interfaces.tool_factory import ToolFactory

class ToolRegistration:
    def __init__(self, manifest: ToolManifest, factory: ToolFactory):
        self.manifest = manifest
        self.factory = factory

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolRegistration] = {}

    def register(self, manifest: ToolManifest, factory: ToolFactory):
        self._tools[manifest.id] = ToolRegistration(manifest, factory)
        
    def get_registration(self, tool_id: str) -> Optional[ToolRegistration]:
        return self._tools.get(tool_id)
        
    def get_all_manifests(self) -> List[ToolManifest]:
        return [reg.manifest for reg in self._tools.values()]
