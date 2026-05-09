pipeline {
    agent any

    parameters {
        booleanParam(name: 'RUN_DEPLOY', defaultValue: false, description: 'Run deploy stage')
        choice(name: 'DEPLOY_ENV', choices: ['staging', 'production'], description: 'Target environment for deployment')
        string(name: 'DEPLOY_IMAGE_TAG', defaultValue: '', description: 'Optional image tag to deploy; leave empty to use current build tag')
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
                    curl -fsS http://127.0.0.1:8000/ready
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
                    env.IMAGE_NAME = 'ghcr.io/nugusu20/ci-cd-lab'
                    env.IMAGE_TAG = sh(
                        script: '''
                            git config --global --add safe.directory /workspace/ci-cd-lab
                            cd /workspace/ci-cd-lab
                            git rev-parse --short HEAD
                        ''',
                        returnStdout: true
                    ).trim()
                    env.REGISTRY_IMAGE = "${env.IMAGE_NAME}:${env.IMAGE_TAG}"

                    if (params.DEPLOY_IMAGE_TAG?.trim()) {
                        env.EFFECTIVE_DEPLOY_TAG = params.DEPLOY_IMAGE_TAG.trim()
                    } else {
                        env.EFFECTIVE_DEPLOY_TAG = env.IMAGE_TAG
                    }

                    env.DEPLOY_ENV_FILE = "deploy/${params.DEPLOY_ENV}.env"
                    env.DEPLOY_ENV_NAME = params.DEPLOY_ENV
                }
                echo "Build image tag: ${env.IMAGE_TAG}"
                echo "Registry-ready image: ${env.REGISTRY_IMAGE}"
                echo "Effective deploy tag: ${env.EFFECTIVE_DEPLOY_TAG}"
                echo "Deploy environment: ${env.DEPLOY_ENV_NAME}"
                echo "Deploy env file: ${env.DEPLOY_ENV_FILE}"
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    cd /workspace/ci-cd-lab
                    docker build -t ci-cd-lab:${IMAGE_TAG} .
                    docker tag ci-cd-lab:${IMAGE_TAG} ${REGISTRY_IMAGE}
                '''
            }
        }

        stage('Write Image Metadata') {
            steps {
                sh '''
                    cd /workspace/ci-cd-lab
                    mkdir -p build
                    printf 'local_image=%s\n' "ci-cd-lab:${IMAGE_TAG}" > build/image-info.txt
                    printf 'registry_image=%s\n' "$REGISTRY_IMAGE" >> build/image-info.txt
                    printf 'effective_deploy_tag=%s\n' "$EFFECTIVE_DEPLOY_TAG" >> build/image-info.txt
                    printf 'deploy_env=%s\n' "$DEPLOY_ENV_NAME" >> build/image-info.txt
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
                      ci-cd-lab:${IMAGE_TAG}
                    sleep 8
                    docker exec ci-cd-lab-jenkins-check python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"
                    docker exec ci-cd-lab-jenkins-check python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/ready').read().decode())"
                    docker exec ci-cd-lab-jenkins-check python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/version').read().decode())"
                    docker inspect --format='{{.State.Health.Status}}' ci-cd-lab-jenkins-check | grep healthy
                    docker stop ci-cd-lab-jenkins-check
                '''
            }
        }

        stage('Approval') {
            when {
                expression { return params.RUN_DEPLOY }
            }
            steps {
                input message: "Approve ${params.DEPLOY_ENV} deploy?", ok: 'Deploy'
            }
        }

        stage('Deploy') {
            when {
                expression { return params.RUN_DEPLOY }
            }
            steps {
                sh '''
                    cd /workspace/ci-cd-lab
                    docker pull ghcr.io/nugusu20/ci-cd-lab:${EFFECTIVE_DEPLOY_TAG}
                    docker compose -f docker-compose.deploy.yml down || true
                    IMAGE_NAME="ghcr.io/nugusu20/ci-cd-lab" IMAGE_TAG="${EFFECTIVE_DEPLOY_TAG}" DEPLOY_ENV_FILE="${DEPLOY_ENV_FILE}" \
                      docker compose -f docker-compose.deploy.yml up -d
                    sleep 8
                    docker inspect --format='{{.State.Health.Status}}' ci-cd-lab-app | grep healthy
                    docker exec ci-cd-lab-nginx wget -qO- http://127.0.0.1/health
                    docker exec ci-cd-lab-nginx wget -qO- http://127.0.0.1/ready
                    docker exec ci-cd-lab-nginx wget -qO- http://127.0.0.1/version

                    mkdir -p deploy-output
                    printf 'deployed_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > deploy-output/deployment.txt
                    printf 'job=%s\n' "$JOB_NAME" >> deploy-output/deployment.txt
                    printf 'build=%s\n' "$BUILD_NUMBER" >> deploy-output/deployment.txt
                    printf 'environment=%s\n' "$DEPLOY_ENV_NAME" >> deploy-output/deployment.txt
                    printf 'version=%s\n' "$EFFECTIVE_DEPLOY_TAG" >> deploy-output/deployment.txt
                    printf 'image=%s:%s\n' "ghcr.io/nugusu20/ci-cd-lab" "$EFFECTIVE_DEPLOY_TAG" >> deploy-output/deployment.txt
                    printf 'registry_image=%s\n' "ghcr.io/nugusu20/ci-cd-lab:${EFFECTIVE_DEPLOY_TAG}" >> deploy-output/deployment.txt
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
