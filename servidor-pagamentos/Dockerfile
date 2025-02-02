FROM maven:3.8.4-jdk-8 AS build

WORKDIR /app

COPY pom.xml .
COPY src ./src
COPY certificados /app/certificados

RUN mvn clean package

FROM openjdk:8-jdk-alpine

WORKDIR /app

COPY --from=build /app/target/servidor-pagamentos-1.0-SNAPSHOT.jar /app/servidor-pagamentos.jar
COPY --from=build /app/target/lib /app/lib

EXPOSE 1099
EXPOSE 9090

CMD ["java", "-cp", "servidor-pagamentos.jar:lib/*", "com.example.Main"]