from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="operator")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    operation_logs = relationship("OperationLog", back_populates="user")
    process_records = relationship("ProcessRecord", back_populates="operator")

class Machine(Base):
    __tablename__ = "machines"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String(50), unique=True, nullable=False, index=True)
    machine_name = Column(String(100), nullable=False)
    machine_type = Column(String(50))
    ip_address = Column(String(50))
    rack = Column(Integer, default=0)
    slot = Column(Integer, default=1)
    status = Column(String(20), default="")
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    process_records = relationship("ProcessRecord", back_populates="machine")
    template = relationship("Template", backref="machines")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(50), unique=True, nullable=False, index=True)
    product_name = Column(String(100), nullable=False)
    product_spec = Column(String(100))
    category = Column(String(50))
    mold_model = Column(String(100))
    cross_section_image = Column(String(255))
    processed_size = Column(String(200))
    weight_per_meter = Column(String(50))
    available_accessories = Column(String(200))
    notes = Column(String(500))
    theoretical_weight_before_grinding = Column(String(50))
    theoretical_weight_after_grinding = Column(String(50))
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    process_records = relationship("ProcessRecord", back_populates="product")

class ProcessRecord(Base):
    __tablename__ = "process_records"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    record_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    notes = Column(Text)
    version = Column(Integer, default=1)  # 版本号
    
    machine = relationship("Machine", back_populates="process_records")
    product = relationship("Product", back_populates="process_records")
    operator = relationship("User", back_populates="process_records")
    parameter_values = relationship("ProcessParameterValue", back_populates="process_record", cascade="all, delete-orphan")

class ProcessParameterValue(Base):
    __tablename__ = "process_parameter_values"
    
    id = Column(Integer, primary_key=True, index=True)
    process_record_id = Column(Integer, ForeignKey("process_records.id", ondelete="CASCADE"), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False, index=True)
    parameter_address = Column(String(50), nullable=False)
    parameter_value = Column(String(50), nullable=False)
    parameter_unit = Column(String(20))
    parameter_type = Column(String(20), nullable=False)
    is_readonly = Column(Boolean, default=False)
    slot = Column(Integer, default=1)
    
    process_record = relationship("ProcessRecord", back_populates="parameter_values")

class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    template_parameters = relationship("TemplateParameter", back_populates="template", cascade="all, delete-orphan")

class TemplateParameter(Base):
    __tablename__ = "template_parameters"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id", ondelete="CASCADE"), nullable=False, index=True)
    parameter_name = Column(String(100), nullable=False, index=True)
    parameter_address = Column(String(50), nullable=False)
    parameter_value = Column(String(100))
    parameter_unit = Column(String(20))
    parameter_type = Column(String(20), default="Int")
    is_readonly = Column(Boolean, default=False)
    slot = Column(Integer, default=1)

    template = relationship("Template", back_populates="template_parameters")

class OperationLog(Base):
    __tablename__ = "operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    operation_type = Column(String(50), index=True)
    target_type = Column(String(50), index=True)
    target_id = Column(Integer)
    details = Column(Text)
    request_params = Column(Text)
    response_data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    user = relationship("User", back_populates="operation_logs")

class AlarmParameter(Base):
    __tablename__ = "alarm_parameters"
    
    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id", ondelete="CASCADE"), nullable=False, index=True)
    alarm_address = Column(String(50), nullable=False, index=True)
    alarm_content = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    machine = relationship("Machine", backref="alarm_parameters")
