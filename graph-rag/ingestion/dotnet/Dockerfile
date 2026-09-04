FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

WORKDIR /src
COPY src/IngestDotNet/IngestDotNet.csproj src/IngestDotNet/
RUN dotnet restore src/IngestDotNet/IngestDotNet.csproj
COPY src/IngestDotNet/ src/IngestDotNet/
RUN dotnet publish src/IngestDotNet/IngestDotNet.csproj -c Release -o /app/publish --no-restore

FROM mcr.microsoft.com/dotnet/sdk:10.0

WORKDIR /app
ENV NUGET_PACKAGES=/tmp/ingest-dotnet-packages
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "IngestDotNet.dll", "--restore"]