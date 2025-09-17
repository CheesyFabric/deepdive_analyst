#!/usr/bin/env groovy
/**
 * DeepDive Analyst - 简化版 Jenkins CI/CD Pipeline
 * 
 * 这是一个简化版本的 Jenkinsfile，适合快速测试和开发环境使用
 * 包含基本的构建、测试和部署流程
 */

pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'deepdive-analyst'
        DOCKER_IMAGE = "${PROJECT_NAME}:${env.BUILD_NUMBER}"
    }
    
    stages {
        // 阶段 1: 代码检出
        stage('📥 Checkout') {
            steps {
                echo "📥 检出代码..."
                checkout scm
            }
        }
        
        // 阶段 2: 环境准备
        stage('🔧 Setup') {
            steps {
                echo "🔧 准备环境..."
                sh '''
                    echo "📊 环境信息:"
                    echo "  - Python 版本: $(python3 --version)"
                    echo "  - Docker 版本: $(docker --version)"
                    echo "  - Git 提交: $(git rev-parse HEAD)"
                '''
            }
        }
        
        // 阶段 3: 安装依赖
        stage('📦 Install Dependencies') {
            steps {
                echo "📦 安装依赖..."
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        // 阶段 4: 代码检查
        stage('🔍 Code Quality') {
            steps {
                echo "🔍 代码质量检查..."
                sh '''
                    source venv/bin/activate
                    
                    # 安装代码检查工具
                    pip install flake8 black
                    
                    # 运行代码检查
                    echo "🎨 运行 flake8..."
                    flake8 src/ --max-line-length=88 || true
                    
                    echo "🎨 运行 black 检查..."
                    black --check src/ || true
                '''
            }
        }
        
        // 阶段 5: 运行测试
        stage('🧪 Test') {
            steps {
                echo "🧪 运行测试..."
                sh '''
                    source venv/bin/activate
                    
                    # 设置测试环境变量
                    export LLM_PROVIDER=openai
                    export LLM_MODEL=gpt-3.5-turbo
                    export OPENAI_API_KEY=test-key
                    
                    # 运行测试
                    pytest tests/ -v --tb=short
                '''
            }
        }
        
        // 阶段 6: 构建 Docker 镜像
        stage('🐳 Build Docker Image') {
            steps {
                echo "🐳 构建 Docker 镜像..."
                sh '''
                    # 构建镜像
                    docker build -t ${DOCKER_IMAGE} .
                    docker build -t ${PROJECT_NAME}:latest .
                    
                    echo "✅ Docker 镜像构建完成"
                    docker images | grep ${PROJECT_NAME}
                '''
            }
        }
        
        // 阶段 7: 测试 Docker 镜像
        stage('🐳 Test Docker Image') {
            steps {
                echo "🐳 测试 Docker 镜像..."
                sh '''
                    # 测试镜像
                    docker run --rm ${DOCKER_IMAGE} python main.py --help
                    docker run --rm ${DOCKER_IMAGE} python main.py version
                    
                    echo "✅ Docker 镜像测试通过"
                '''
            }
        }
    }
    
    post {
        always {
            echo "🧹 清理工作空间..."
            cleanWs()
        }
        
        success {
            echo "🎉 构建成功！"
        }
        
        failure {
            echo "❌ 构建失败！"
        }
    }
}
