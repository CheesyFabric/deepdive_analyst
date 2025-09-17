pipeline {
    agent any   // 在任意节点上运行

    stages {
        stage('Build') {
            steps {
                echo "=== 构建中... ==="
                sh 'echo "模拟构建完成"'
            }
        }

        stage('Test') {
            steps {
                echo "=== 执行测试 ==="
                sh 'echo "模拟测试通过"'
            }
        }

        stage('Deploy') {
            steps {
                echo "=== 部署阶段 ==="
                sh 'echo "模拟部署完成"'
            }
        }
    }

    post {
        success {
            echo '✅ 流水线执行成功！'
        }
        failure {
            echo ' 流水线执行失败！'
        }
    }
}