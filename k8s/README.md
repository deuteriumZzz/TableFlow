# Kubernetes Deployment

## Prerequisites
- kubectl configured for your cluster
- Docker images built and pushed to a registry

## Build & Push Images

```bash
REGISTRY=your-registry.io/tableflow

docker build -t $REGISTRY/backend:latest ./backend
docker build -t $REGISTRY/frontend:latest ./frontend

docker push $REGISTRY/backend:latest
docker push $REGISTRY/frontend:latest
```

Update the `image:` fields in `k8s/backend/deployment.yaml` and `k8s/frontend/deployment.yaml`.

## Deploy

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml
```

## Seed initial data (first deploy only)

```bash
POD=$(kubectl get pod -n tableflow -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n tableflow $POD -- python manage.py shell -c "
from apps.accounts.models import User
from apps.restaurants.models import Restaurant
from apps.tables.models import Table
from apps.payments.models import PaymentMethod
from apps.menu.models import Category, Product

if not Restaurant.objects.exists():
    r = Restaurant.objects.create(name='TableFlow', address='ул. Примерная, 1', phone='+7000000000', email='admin@tableflow.ru', currency='RUB')
    User.objects.create_superuser('admin', 'admin@tableflow.ru', 'CHANGE_ME', role='admin', restaurant=r)
    for i in range(1, 11):
        Table.objects.create(restaurant=r, number=i, capacity=4)
    PaymentMethod.objects.create(name='Наличные')
    PaymentMethod.objects.create(name='Банковская карта')
    print('Seed OK')
"
```

## Update secrets for production

```bash
kubectl create secret generic backend-secret \
  --from-literal=SECRET_KEY='your-real-secret-key' \
  --from-literal=DATABASE_URL='postgresql://user:pass@postgres:5432/tableflow' \
  -n tableflow --dry-run=client -o yaml | kubectl apply -f -
```

## Check deployment status

```bash
kubectl get all -n tableflow
kubectl logs -n tableflow -l app=backend --tail=50
```
