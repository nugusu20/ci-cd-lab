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
                sh '''
                    cd /workspace/ci-cd-lab
                    python3 -m app.main &
                    sleep 2
                    curl -fsS http://127.0.0.1:8000/health
                    curl -fsS http://127.0.0.1:8000/version
                    pkill -f "python3 -m app.main" || true
                '''
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

        stage('Set Image Tag') {
            steps {
                script {
                    env.IMAGE_NAME = 'ci-cd-lab'
                    env.IMAGE_TAG = sh(
                        script: '''
                            git config --global --add safe.directory /workspace/ci-cd-lab
                            cd /workspace/ci-cd-lab
                            git rev-parse --short HEAD
                        ''',
                        returnStdout: true
                    ).trim()
                }
                echo "Using image tag: ${env.IMAGE_TAG}"
            }
        }

        stage('Docker Build') {
            steps {
                sh 'cd /workspace/ci-cd-lab && docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .'
            }
        }

        stage('Write Image Metadata') {
            steps {
                sh '''
                    cd /workspace/ci-cd-lab
                    mkdir -p build
                    printf 'image=%s:%s\n' "$IMAGE_NAME" "$IMAGE_TAG" > build/image-info.txt
                    cat build/image-info.txt
                '''
            }
        }

        stage('Container Health Check') {
            steps {
                sh '''
                    docker rm -f ci-cd-lab-jenkins-check 2>/dev/null || true
                    docker run -d --rm --name ci-cd-lab-jenkins-check \
                      -e APP_VERSION="${IMAGE_TAG}" \
                      -e IMAGE_TAG="${IMAGE_TAG}" \
                      ${IMAGE_NAME}:${IMAGE_TAG}
                    sleep 3
                    docker exec ci-cd-lab-jenkins-check python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"
                    docker exec ci-cd-lab-jenkins-check python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/version').read().decode())"
                    docker stop ci-cd-lab-jenkins-check
                '''
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
                    printf 'version=%s\n' "$IMAGE_TAG" >> deploy-output/deployment.txt
                    printf 'image=%s:%s\n' "$IMAGE_NAME" "$IMAGE_TAG" >> deploy-output/deployment.txt
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
