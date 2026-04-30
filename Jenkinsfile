pipeline {
    agent any

    parameters {
        booleanParam(name: 'RUN_DEPLOY', defaultValue: false, description: 'Run deploy stage')
    }

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

        stage('Approval') {
            when {
                expression { return params.RUN_DEPLOY }
            }
            steps {
                input message: 'Approve deploy?', ok: 'Deploy'
            }
        }

        stage('Deploy') {
            when {
                expression { return params.RUN_DEPLOY }
            }
            steps {
                sh '''
                    cd /workspace/ci-cd-lab
                    mkdir -p deploy-output
                    printf 'deployed_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > deploy-output/deployment.txt
                    printf 'job=%s\n' "$JOB_NAME" >> deploy-output/deployment.txt
                    printf 'build=%s\n' "$BUILD_NUMBER" >> deploy-output/deployment.txt
                    cat deploy-output/deployment.txt
                '''
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
