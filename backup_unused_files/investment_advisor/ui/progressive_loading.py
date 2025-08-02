"""
Progressive Loading UI Components

Implements progressive loading patterns for better user experience.
"""

import streamlit as st
import time
import threading
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


@dataclass
class LoadingStep:
    """Represents a single loading step."""
    
    name: str
    description: str
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    weight: float = 1.0  # Relative weight for progress calculation
    required: bool = True  # Whether failure should stop the process
    estimated_time: Optional[float] = None  # Estimated time in seconds
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


class ProgressiveLoader:
    """
    Manages progressive loading of multiple components with real-time updates.
    """
    
    def __init__(self, title: str = "분석 진행 중"):
        self.title = title
        self.steps: List[LoadingStep] = []
        self.results: Dict[str, Any] = {}
        self.errors: Dict[str, Exception] = {}
        self.current_step = 0
        self.total_weight = 0
        self.completed_weight = 0
        
        # UI components
        self.progress_container = None
        self.status_container = None
        self.progress_bar = None
        self.status_text = None
        self.step_details = None
        
    def add_step(
        self,
        name: str,
        description: str,
        function: Callable,
        args: tuple = (),
        kwargs: dict = None,
        weight: float = 1.0,
        required: bool = True,
        estimated_time: Optional[float] = None
    ):
        """Add a loading step."""
        step = LoadingStep(
            name=name,
            description=description,
            function=function,
            args=args,
            kwargs=kwargs or {},
            weight=weight,
            required=required,
            estimated_time=estimated_time
        )
        self.steps.append(step)
        self.total_weight += weight
    
    def create_ui(self):
        """Create the progressive loading UI."""
        # Main container with professional styling
        st.markdown("""
        <div class="professional-info-box fade-in" style="text-align: center; margin: 2rem 0;">
            <h3 style="color: #2C3E50; margin-bottom: 1rem;">{}</h3>
        </div>
        """.format(self.title), unsafe_allow_html=True)
        
        # Progress container
        self.progress_container = st.empty()
        
        # Status container
        self.status_container = st.empty()
        
        # Step details container (initially hidden)
        self.step_details = st.empty()
        
        # Initialize progress display
        self._update_progress(0, "초기화 중...")
    
    def _update_progress(self, progress: float, status: str, step_info: str = ""):
        """Update progress display."""
        if self.progress_container is None:
            return
        
        with self.progress_container.container():
            # Progress bar with gradient
            st.markdown(f"""
            <div style="
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 4px;
                margin: 20px 0;
            ">
                <div style="
                    width: {progress}%;
                    height: 12px;
                    background: linear-gradient(90deg, #4ECDC4, #26C6DA);
                    border-radius: 16px;
                    transition: width 0.5s ease-in-out;
                    position: relative;
                ">
                    <div style="
                        position: absolute;
                        right: 8px;
                        top: 50%;
                        transform: translateY(-50%);
                        color: white;
                        font-size: 10px;
                        font-weight: 600;
                    ">
                        {progress:.0f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with self.status_container.container():
            st.markdown(f"""
            <div style="
                text-align: center;
                color: #7F8C8D;
                font-size: 16px;
                margin: 10px 0;
            ">
                {status}
            </div>
            """, unsafe_allow_html=True)
        
        if step_info and self.step_details:
            with self.step_details.container():
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 12px;
                    margin: 10px 0;
                    color: #95A5A6;
                    font-size: 14px;
                    text-align: center;
                ">
                    {step_info}
                </div>
                """, unsafe_allow_html=True)
    
    def _create_skeleton_placeholder(self, component_type: str):
        """Create skeleton loading placeholder."""
        if component_type == "chart":
            st.markdown("""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                height: 400px;
                margin: 20px 0;
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                    animation: shimmer 2s infinite;
                "></div>
            </div>
            <style>
            @keyframes shimmer {
                100% { left: 100%; }
            }
            </style>
            """, unsafe_allow_html=True)
        
        elif component_type == "metrics":
            cols = st.columns(4)
            for i, col in enumerate(cols):
                with col:
                    st.markdown(f"""
                    <div style="
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 12px;
                        height: 100px;
                        margin: 10px 0;
                        position: relative;
                        overflow: hidden;
                        animation: pulse 2s infinite {i * 0.2}s;
                    ">
                        <div style="
                            padding: 20px;
                            text-align: center;
                        ">
                            <div style="
                                width: 60%;
                                height: 12px;
                                background: rgba(255,255,255,0.1);
                                border-radius: 6px;
                                margin: 10px auto;
                            "></div>
                            <div style="
                                width: 80%;
                                height: 20px;
                                background: rgba(255,255,255,0.1);
                                border-radius: 10px;
                                margin: 15px auto;
                            "></div>
                        </div>
                    </div>
                    <style>
                    @keyframes pulse {{
                        0%, 100% {{ opacity: 0.3; }}
                        50% {{ opacity: 0.6; }}
                    }}
                    </style>
                    """, unsafe_allow_html=True)
        
        elif component_type == "text":
            st.markdown("""
            <div style="
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
            ">
                <div style="
                    width: 30%;
                    height: 16px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 8px;
                    margin: 10px 0;
                "></div>
                <div style="
                    width: 90%;
                    height: 12px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 6px;
                    margin: 8px 0;
                "></div>
                <div style="
                    width: 75%;
                    height: 12px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 6px;
                    margin: 8px 0;
                "></div>
                <div style="
                    width: 85%;
                    height: 12px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 6px;
                    margin: 8px 0;
                "></div>
            </div>
            """, unsafe_allow_html=True)
    
    def run_sequential(self) -> Dict[str, Any]:
        """Run steps sequentially with progress updates."""
        if not self.steps:
            return {}
        
        self.create_ui()
        
        for i, step in enumerate(self.steps):
            self.current_step = i
            
            # Update progress
            progress = (self.completed_weight / self.total_weight) * 100
            self._update_progress(
                progress,
                f"단계 {i + 1}/{len(self.steps)}: {step.description}",
                f"예상 소요시간: {step.estimated_time or '알 수 없음'}초" if step.estimated_time else ""
            )
            
            try:
                # Execute step
                start_time = time.time()
                result = step.function(*step.args, **step.kwargs)
                execution_time = time.time() - start_time
                
                # Store result
                self.results[step.name] = result
                self.completed_weight += step.weight
                
                logger.info(f"Completed step '{step.name}' in {execution_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Step '{step.name}' failed: {e}")
                self.errors[step.name] = e
                
                if step.required:
                    # Update progress to show error
                    self._update_progress(
                        progress,
                        f"오류 발생: {step.description}",
                        f"오류 내용: {str(e)}"
                    )
                    raise
                else:
                    # Continue with optional step failure
                    self.completed_weight += step.weight
        
        # Final progress update
        self._update_progress(100, "분석 완료!")
        
        # Clear loading UI after a brief pause
        time.sleep(1)
        if self.progress_container:
            self.progress_container.empty()
        if self.status_container:
            self.status_container.empty()
        if self.step_details:
            self.step_details.empty()
        
        return self.results
    
    def run_parallel(self, max_workers: int = 3) -> Dict[str, Any]:
        """Run steps in parallel where possible."""
        if not self.steps:
            return {}
        
        self.create_ui()
        
        # Separate required and optional steps
        required_steps = [step for step in self.steps if step.required]
        optional_steps = [step for step in self.steps if not step.required]
        
        # Execute required steps first
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit required steps
            future_to_step = {
                executor.submit(step.function, *step.args, **step.kwargs): step
                for step in required_steps
            }
            
            # Process completed steps
            for future in as_completed(future_to_step):
                step = future_to_step[future]
                
                try:
                    result = future.result()
                    self.results[step.name] = result
                    self.completed_weight += step.weight
                    
                    # Update progress
                    progress = (self.completed_weight / self.total_weight) * 100
                    self._update_progress(
                        progress,
                        f"{step.description} 완료",
                        f"남은 작업: {len(self.steps) - len(self.results)}개"
                    )
                    
                except Exception as e:
                    logger.error(f"Required step '{step.name}' failed: {e}")
                    self.errors[step.name] = e
                    raise
        
        # Execute optional steps
        if optional_steps:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_step = {
                    executor.submit(step.function, *step.args, **step.kwargs): step
                    for step in optional_steps
                }
                
                for future in as_completed(future_to_step):
                    step = future_to_step[future]
                    
                    try:
                        result = future.result()
                        self.results[step.name] = result
                    except Exception as e:
                        logger.warning(f"Optional step '{step.name}' failed: {e}")
                        self.errors[step.name] = e
                    
                    self.completed_weight += step.weight
                    progress = (self.completed_weight / self.total_weight) * 100
                    self._update_progress(progress, f"{step.description} 처리됨")
        
        # Final progress update
        self._update_progress(100, "모든 분석 완료!")
        
        # Clear loading UI
        time.sleep(1)
        if self.progress_container:
            self.progress_container.empty()
        if self.status_container:
            self.status_container.empty()
        if self.step_details:
            self.step_details.empty()
        
        return self.results


class LazyLoader:
    """Lazy loading component for heavy UI elements."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_loaded = False
        self.content = None
        self.placeholder = None
    
    def create_placeholder(self, placeholder_type: str = "generic"):
        """Create a placeholder while content loads."""
        self.placeholder = st.empty()
        
        with self.placeholder.container():
            if placeholder_type == "chart":
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
                    border-radius: 16px;
                    height: 400px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border: 1px solid rgba(255,255,255,0.1);
                ">
                    <div style="
                        text-align: center;
                        color: #7F8C8D;
                    ">
                        <div style="
                            width: 40px;
                            height: 40px;
                            border: 3px solid rgba(78, 205, 196, 0.3);
                            border-top: 3px solid #4ECDC4;
                            border-radius: 50%;
                            animation: spin 1s linear infinite;
                            margin: 0 auto 16px;
                        "></div>
                        <div>차트 로딩 중...</div>
                    </div>
                </div>
                <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                </style>
                """, unsafe_allow_html=True)
            
            elif placeholder_type == "table":
                st.markdown("""
                <div style="
                    background: rgba(255,255,255,0.05);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    color: #7F8C8D;
                ">
                    <div style="
                        display: inline-block;
                        width: 20px;
                        height: 20px;
                        border: 2px solid rgba(78, 205, 196, 0.3);
                        border-top: 2px solid #4ECDC4;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin-right: 10px;
                    "></div>
                    데이터 로딩 중...
                </div>
                """, unsafe_allow_html=True)
    
    def load_content(self, content_function: Callable, *args, **kwargs):
        """Load actual content and replace placeholder."""
        if self.is_loaded:
            return self.content
        
        try:
            # Execute content function
            self.content = content_function(*args, **kwargs)
            self.is_loaded = True
            
            # Replace placeholder with actual content
            if self.placeholder:
                with self.placeholder.container():
                    if callable(self.content):
                        self.content()
                    else:
                        st.write(self.content)
            
            return self.content
            
        except Exception as e:
            logger.error(f"Failed to load content for {self.name}: {e}")
            if self.placeholder:
                with self.placeholder.container():
                    st.error(f"콘텐츠 로딩 실패: {str(e)}")
            raise
    
    def clear(self):
        """Clear the loaded content."""
        if self.placeholder:
            self.placeholder.empty()
        self.is_loaded = False
        self.content = None


def create_loading_animation(animation_type: str = "spinner"):
    """Create loading animation component."""
    if animation_type == "spinner":
        return st.markdown("""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
        ">
            <div style="
                width: 40px;
                height: 40px;
                border: 4px solid rgba(78, 205, 196, 0.3);
                border-top: 4px solid #4ECDC4;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            "></div>
        </div>
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>
        """, unsafe_allow_html=True)
    
    elif animation_type == "dots":
        return st.markdown("""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
        ">
            <div style="
                display: flex;
                gap: 8px;
            ">
                <div style="
                    width: 12px;
                    height: 12px;
                    background: #4ECDC4;
                    border-radius: 50%;
                    animation: bounce 1.4s infinite ease-in-out both;
                    animation-delay: -0.32s;
                "></div>
                <div style="
                    width: 12px;
                    height: 12px;
                    background: #4ECDC4;
                    border-radius: 50%;
                    animation: bounce 1.4s infinite ease-in-out both;
                    animation-delay: -0.16s;
                "></div>
                <div style="
                    width: 12px;
                    height: 12px;
                    background: #4ECDC4;
                    border-radius: 50%;
                    animation: bounce 1.4s infinite ease-in-out both;
                "></div>
            </div>
        </div>
        <style>
        @keyframes bounce {
            0%, 80%, 100% {
                transform: scale(0);
            } 40% {
                transform: scale(1.0);
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    elif animation_type == "pulse":
        return st.markdown("""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px;
        ">
            <div style="
                width: 60px;
                height: 60px;
                background: #4ECDC4;
                border-radius: 50%;
                animation: pulse 2s infinite;
                opacity: 0.6;
            "></div>
        </div>
        <style>
        @keyframes pulse {
            0% {
                transform: scale(0);
                opacity: 1;
            }
            100% {
                transform: scale(1);
                opacity: 0;
            }
        }
        </style>
        """, unsafe_allow_html=True)