pipeline {
    agent any

    stages {
        stage('Prepare') {
            steps {
                sh 'cd /workspace/ci-cd-lab && pwd && ls -la'
            }
        }

        stage('Smoke') {
            steps {
                sh 'cd /workspace/ci-cd-lab && python3 app/main.py'
            }
        }

        stage('Lint') {
            steps {
                sh 'cd /workspace/ci-cd-lab && python3 -m flake8 app tests'
            }
        }

        stage('Test') {
            steps {
                sh 'cd /workspace/ci-cd-lab && python3 -m pytest tests/'
            }
        }
    }

    post {
        always {
            echo 'Jenkinsfile pipeline finished'
        }
        success {
            echo 'Jenkinsfile pipeline succeeded'
        }
        failure {
            echo 'Jenkinsfile pipeline failed'
        }
    }
}
