#!/usr/bin/env python3
"""
ASMF v2.1 Production System - Main Package Initialization
Advanced Semantic Memory Framework with GPU acceleration, Enhanced Storage, and LLM integration

Author: Serhii Stepanov (Baden-Baden, Germany)
Repository: https://github.com/Serhii-Stepanov-Baden-Baden/ASMF-V2-production
Version: 2.1.0
"""

import sys
import logging
from typing import Optional, Dict, Any, List

# Version Information
__version__ = "2.1.0"
__author__ = "Serhii Stepanov"
__description__ = "ASMF v2.1 - Advanced Semantic Memory Framework with GPU/LLM/Enhanced Storage"

# Core version constants for v2.1
CORE_VERSION = "2.1.0"
V2_1_RELEASE_DATE = "2025-11-22"
REPOSITORY_URL = "https://github.com/Serhii-Stepanov-Baden-Baden/ASMF-V2-production"

# v2.1 Feature Availability Flags
GPU_AVAILABLE = False
STORAGE_AVAILABLE = False
LLM_AVAILABLE = False
ENHANCED_ANALYTICS_AVAILABLE = False

# v2.1 Module Import Status
V2_1_MODULES_IMPORTED = {
    'advanced_recovery': False,
    'smart_session_manager': False,
    'mega_project_integrator': False,
    'emotional_companion': False,
    'main_application': False,
    'database_optimization': False,
    'gpu_support': False
}

# Fallback module availability (v2.0 compatibility)
V2_0_FALLBACK_AVAILABLE = {
    'advanced_recovery': False,
    'smart_session_manager': False,
    'mega_project_integrator': False,
    'emotional_companion': False,
    'main': False
}

# Configure logging for package initialization
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def _log_module_status(module_name: str, available: bool, version: str = "unknown"):
    """Log module availability status"""
    status = "✅ Available" if available else "❌ Not Available"
    logger.info(f"ASMF {module_name}: {status} (v{version})")

# =============================================================================
# v2.1 Module Imports with Fallback Mechanisms
# =============================================================================

def _import_v2_1_modules():
    """Import all v2.1 modules with comprehensive fallback"""
    global GPU_AVAILABLE, STORAGE_AVAILABLE, LLM_AVAILABLE, ENHANCED_ANALYTICS_AVAILABLE
    
    # Import Advanced Recovery System v2.1
    try:
        from advanced_recovery_v2_1 import AdvancedRecoverySystem
        V2_1_MODULES_IMPORTED['advanced_recovery'] = True
        V2_0_FALLBACK_AVAILABLE['advanced_recovery'] = False
        _log_module_status("Advanced Recovery", True, "2.1.0")
    except ImportError as e:
        try:
            from advanced_recovery import AdvancedRecoverySystem
            V2_0_FALLBACK_AVAILABLE['advanced_recovery'] = True
            logger.warning(f"Using v2.0 fallback for Advanced Recovery: {e}")
            _log_module_status("Advanced Recovery", True, "2.0.0 (fallback)")
        except ImportError:
            logger.error("Advanced Recovery module not found")
            _log_module_status("Advanced Recovery", False)
    
    # Import Smart Session Manager v2.1
    try:
        from smart_session_manager_v2_1 import SmartSessionManager
        V2_1_MODULES_IMPORTED['smart_session_manager'] = True
        V2_0_FALLBACK_AVAILABLE['smart_session_manager'] = False
        _log_module_status("Smart Session Manager", True, "2.1.0")
    except ImportError as e:
        try:
            from smart_session_manager import SmartSessionManager
            V2_0_FALLBACK_AVAILABLE['smart_session_manager'] = True
            logger.warning(f"Using v2.0 fallback for Smart Session Manager: {e}")
            _log_module_status("Smart Session Manager", True, "2.0.0 (fallback)")
        except ImportError:
            logger.error("Smart Session Manager module not found")
            _log_module_status("Smart Session Manager", False)
    
    # Import Mega Project Integrator v2.1
    try:
        from mega_project_integrator_v2_1 import MegaProjectIntegrator
        V2_1_MODULES_IMPORTED['mega_project_integrator'] = True
        V2_0_FALLBACK_AVAILABLE['mega_project_integrator'] = False
        _log_module_status("Mega Project Integrator", True, "2.1.0")
    except ImportError as e:
        try:
            from mega_project_integrator import MegaProjectIntegrator
            V2_0_FALLBACK_AVAILABLE['mega_project_integrator'] = True
            logger.warning(f"Using v2.0 fallback for Mega Project Integrator: {e}")
            _log_module_status("Mega Project Integrator", True, "2.0.0 (fallback)")
        except ImportError:
            logger.error("Mega Project Integrator module not found")
            _log_module_status("Mega Project Integrator", False)
    
    # Import Emotional Companion v2.1
    try:
        from emotional_companion_v2_1 import EmotionalCompanion
        V2_1_MODULES_IMPORTED['emotional_companion'] = True
        V2_0_FALLBACK_AVAILABLE['emotional_companion'] = False
        _log_module_status("Emotional Companion", True, "2.1.0")
    except ImportError as e:
        try:
            from emotional_companion import EmotionalCompanion
            V2_0_FALLBACK_AVAILABLE['emotional_companion'] = True
            logger.warning(f"Using v2.0 fallback for Emotional Companion: {e}")
            _log_module_status("Emotional Companion", True, "2.0.0 (fallback)")
        except ImportError:
            logger.error("Emotional Companion module not found")
            _log_module_status("Emotional Companion", False)
    
    # Import Main Application (ASMF v2.1)
    try:
        from main_v2_1 import ASMFApplication
        V2_1_MODULES_IMPORTED['main_application'] = True
        V2_0_FALLBACK_AVAILABLE['main'] = False
        _log_module_status("ASMF Application", True, "2.1.0")
    except ImportError as e:
        try:
            from main import ASMFApplication
            V2_0_FALLBACK_AVAILABLE['main'] = True
            logger.warning(f"Using v2.0 fallback for Main Application: {e}")
            _log_module_status("ASMF Application", True, "2.0.0 (fallback)")
        except ImportError:
            logger.error("Main Application module not found")
            _log_module_status("ASMF Application", False)
    
    # Import support modules
    try:
        import database_optimization
        V2_1_MODULES_IMPORTED['database_optimization'] = True
        _log_module_status("Database Optimization", True)
        STORAGE_AVAILABLE = True
    except ImportError:
        logger.warning("Database optimization module not found")
        _log_module_status("Database Optimization", False)
    
    try:
        import gpu_support
        V2_1_MODULES_IMPORTED['gpu_support'] = True
        _log_module_status("GPU Support", True)
        GPU_AVAILABLE = True
    except ImportError:
        logger.warning("GPU support module not found")
        _log_module_status("GPU Support", False)
    
    # Check for Enhanced Analytics availability
    ENHANCED_ANALYTICS_AVAILABLE = all([
        V2_1_MODULES_IMPORTED['advanced_recovery'],
        V2_1_MODULES_IMPORTED['smart_session_manager'],
        V2_1_MODULES_IMPORTED['mega_project_integrator']
    ])
    
    # Update LLM availability based on v2.1 modules
    LLM_AVAILABLE = V2_1_MODULES_IMPORTED['advanced_recovery'] or V2_1_MODULES_IMPORTED['emotional_companion']

# =============================================================================
# Core Exports
# =============================================================================

# Import all modules with fallback
_import_v2_1_modules()

# Export main classes with version awareness
def get_advanced_recovery():
    """Get Advanced Recovery System (v2.1 with v2.0 fallback)"""
    if V2_1_MODULES_IMPORTED['advanced_recovery']:
        from advanced_recovery_v2_1 import AdvancedRecoverySystem
        return AdvancedRecoverySystem
    elif V2_0_FALLBACK_AVAILABLE['advanced_recovery']:
        from advanced_recovery import AdvancedRecoverySystem
        return AdvancedRecoverySystem
    else:
        raise ImportError("Advanced Recovery System not available")

def get_smart_session_manager():
    """Get Smart Session Manager (v2.1 with v2.0 fallback)"""
    if V2_1_MODULES_IMPORTED['smart_session_manager']:
        from smart_session_manager_v2_1 import SmartSessionManager
        return SmartSessionManager
    elif V2_0_FALLBACK_AVAILABLE['smart_session_manager']:
        from smart_session_manager import SmartSessionManager
        return SmartSessionManager
    else:
        raise ImportError("Smart Session Manager not available")

def get_mega_project_integrator():
    """Get Mega Project Integrator (v2.1 with v2.0 fallback)"""
    if V2_1_MODULES_IMPORTED['mega_project_integrator']:
        from mega_project_integrator_v2_1 import MegaProjectIntegrator
        return MegaProjectIntegrator
    elif V2_0_FALLBACK_AVAILABLE['mega_project_integrator']:
        from mega_project_integrator import MegaProjectIntegrator
        return MegaProjectIntegrator
    else:
        raise ImportError("Mega Project Integrator not available")

def get_emotional_companion():
    """Get Emotional Companion (v2.1 with v2.0 fallback)"""
    if V2_1_MODULES_IMPORTED['emotional_companion']:
        from emotional_companion_v2_1 import EmotionalCompanion
        return EmotionalCompanion
    elif V2_0_FALLBACK_AVAILABLE['emotional_companion']:
        from emotional_companion import EmotionalCompanion
        return EmotionalCompanion
    else:
        raise ImportError("Emotional Companion not available")

def get_asmf_application():
    """Get ASMF Main Application (v2.1 with v2.0 fallback)"""
    if V2_1_MODULES_IMPORTED['main_application']:
        from main_v2_1 import ASMFApplication
        return ASMFApplication
    elif V2_0_FALLBACK_AVAILABLE['main']:
        from main import ASMFApplication
        return ASMFApplication
    else:
        raise ImportError("ASMF Application not available")

# =============================================================================
# v2.1 System Information
# =============================================================================

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive ASMF v2.1 system information"""
    return {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "core_version": CORE_VERSION,
        "release_date": V2_1_RELEASE_DATE,
        "repository": REPOSITORY_URL,
        "v2_1_features": {
            "gpu_acceleration": GPU_AVAILABLE,
            "enhanced_storage": STORAGE_AVAILABLE,
            "llm_integration": LLM_AVAILABLE,
            "enhanced_analytics": ENHANCED_ANALYTICS_AVAILABLE
        },
        "module_status": V2_1_MODULES_IMPORTED.copy(),
        "fallback_status": V2_0_FALLBACK_AVAILABLE.copy(),
        "available_components": {
            "advanced_recovery": V2_1_MODULES_IMPORTED['advanced_recovery'] or V2_0_FALLBACK_AVAILABLE['advanced_recovery'],
            "smart_session_manager": V2_1_MODULES_IMPORTED['smart_session_manager'] or V2_0_FALLBACK_AVAILABLE['smart_session_manager'],
            "mega_project_integrator": V2_1_MODULES_IMPORTED['mega_project_integrator'] or V2_0_FALLBACK_AVAILABLE['mega_project_integrator'],
            "emotional_companion": V2_1_MODULES_IMPORTED['emotional_companion'] or V2_0_FALLBACK_AVAILABLE['emotional_companion'],
            "main_application": V2_1_MODULES_IMPORTED['main_application'] or V2_0_FALLBACK_AVAILABLE['main']
        }
    }

def print_system_status():
    """Print comprehensive ASMF v2.1 system status"""
    info = get_system_info()
    
    print("\n" + "="*60)
    print(f"ASMF v{info['version']} - System Status")
    print("="*60)
    print(f"Author: {info['author']}")
    print(f"Repository: {info['repository']}")
    print(f"Release Date: {info['release_date']}")
    print()
    
    print("🔧 v2.1 Advanced Features:")
    for feature, available in info['v2_1_features'].items():
        status = "✅ Enabled" if available else "❌ Disabled"
        feature_name = feature.replace('_', ' ').title()
        print(f"  {feature_name}: {status}")
    print()
    
    print("📦 Module Status:")
    for component, available in info['available_components'].items():
        status = "✅ Available" if available else "❌ Not Available"
        component_name = component.replace('_', ' ').title()
        print(f"  {component_name}: {status}")
    print()
    
    print("🔄 Fallback Compatibility:")
    v2_0_fallbacks = sum(info['fallback_status'].values())
    total_fallbacks = len(info['fallback_status'])
    print(f"  v2.0 Compatibility: {v2_0_fallbacks}/{total_fallbacks} modules")
    print()
    
    print("="*60)

# =============================================================================
# Main exports for easy importing
# =============================================================================

__all__ = [
    # Version information
    '__version__',
    '__author__', 
    '__description__',
    
    # Core classes (latest available version)
    'AdvancedRecoverySystem',
    'SmartSessionManager', 
    'MegaProjectIntegrator',
    'EmotionalCompanion',
    'ASMFApplication',
    
    # Utility functions
    'get_system_info',
    'print_system_status',
    
    # Feature flags
    'GPU_AVAILABLE',
    'STORAGE_AVAILABLE', 
    'LLM_AVAILABLE',
    'ENHANCED_ANALYTICS_AVAILABLE',
    
    # Status dictionaries
    'V2_1_MODULES_IMPORTED',
    'V2_0_FALLBACK_AVAILABLE'
]

# Auto-export main classes with version awareness
AdvancedRecoverySystem = get_advanced_recovery()
SmartSessionManager = get_smart_session_manager()
MegaProjectIntegrator = get_mega_project_integrator()
EmotionalCompanion = get_emotional_companion()
ASMFApplication = get_asmf_application()

# Log successful initialization
logger.info(f"ASMF v{__version__} package initialization complete")
if __name__ == "__main__":
    print_system_status()
